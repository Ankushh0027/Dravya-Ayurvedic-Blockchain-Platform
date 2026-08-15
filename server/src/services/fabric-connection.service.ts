import * as grpc from '@grpc/grpc-js';
import { connect, Contract, Identity, Signer, signers } from '@hyperledger/fabric-gateway';
import * as crypto from 'crypto';
import { promises as fs } from 'fs';
import * as path from 'path';
import { Role } from '@prisma/client';

export class FabricConnectionService {
  private static readonly channelName = process.env.FABRIC_CHANNEL || 'dravya-channel';
  private static readonly chaincodeName = process.env.FABRIC_CHAINCODE || 'traceability';
  
  // Hardcoded for the local test-network prototype. In production, these would be in env vars.
  private static readonly mspIdOrg1 = 'Org1MSP';
  private static readonly mspIdOrg2 = 'Org2MSP';
  private static readonly mspIdOrg3 = 'Org3MSP';
  
  private static readonly networkDir = path.resolve(__dirname, '../../../blockchain/fabric-samples/test-network');

  /**
   * Determine the Fabric Organization based on the Application Role.
   */
  public static getOrgForRole(role: Role): string {
    switch (role) {
      case Role.VERIFICATION_AUTHORITY:
        return 'org1.example.com';
      case Role.LAB:
        return 'org2.example.com';
      case Role.ADMIN:
      case Role.PRODUCER:
      case Role.DISTRIBUTOR:
        return 'org3.example.com';
      default:
        return 'org3.example.com'; // Default to platform
    }
  }

  public static getMspIdForRole(role: Role): string {
    const org = this.getOrgForRole(role);
    if (org === 'org1.example.com') return this.mspIdOrg1;
    if (org === 'org2.example.com') return this.mspIdOrg2;
    return this.mspIdOrg3;
  }

  private static async newGrpcConnection(org: string): Promise<grpc.Client> {
    let peerEndpoint = 'localhost:7051';
    let peerHostAlias = 'peer0.org1.example.com';
    if (org === 'org2.example.com') {
      peerEndpoint = 'localhost:9051';
      peerHostAlias = 'peer0.org2.example.com';
    } else if (org === 'org3.example.com') {
      peerEndpoint = 'localhost:11051';
      peerHostAlias = 'peer0.org3.example.com';
    }

    const tlsCertPath = path.join(
      this.networkDir,
      `organizations/peerOrganizations/${org}/peers/${peerHostAlias}/tls/ca.crt`
    );

    const tlsRootCert = await fs.readFile(tlsCertPath);
    const tlsCredentials = grpc.credentials.createSsl(tlsRootCert);
    return new grpc.Client(peerEndpoint, tlsCredentials, {
      'grpc.ssl_target_name_override': peerHostAlias,
    });
  }

  private static async newIdentity(org: string): Promise<Identity> {
    const certPath = path.join(
      this.networkDir,
      `organizations/peerOrganizations/${org}/users/User1@${org}/msp/signcerts`
    );
    const files = await fs.readdir(certPath);
    const cert = await fs.readFile(path.join(certPath, files[0]));
    
    let mspId = this.mspIdOrg1;
    if (org === 'org2.example.com') mspId = this.mspIdOrg2;
    if (org === 'org3.example.com') mspId = this.mspIdOrg3;
    
    return { mspId, credentials: cert };
  }

  private static async newSigner(org: string): Promise<Signer> {
    const keyPath = path.join(
      this.networkDir,
      `organizations/peerOrganizations/${org}/users/User1@${org}/msp/keystore`
    );
    const files = await fs.readdir(keyPath);
    const key = await fs.readFile(path.join(keyPath, files[0]));
    const privateKey = crypto.createPrivateKey(key);
    return signers.newPrivateKeySigner(privateKey);
  }

  /**
   * Connect to the Fabric network and return the Contract and a cleanup function.
   */
  public static async getContractForRole(role: Role): Promise<{ contract: Contract, close: () => void }> {
    const org = this.getOrgForRole(role);
    const client = await this.newGrpcConnection(org);
    const gateway = connect({
      client,
      identity: await this.newIdentity(org),
      signer: await this.newSigner(org),
      // Default timeouts for testing
      evaluateOptions: () => ({ deadline: Date.now() + 5000 }),
      endorseOptions: () => ({ deadline: Date.now() + 15000 }),
      submitOptions: () => ({ deadline: Date.now() + 5000 }),
      commitStatusOptions: () => ({ deadline: Date.now() + 60000 }),
    });

    const network = gateway.getNetwork(this.channelName);
    const contract = network.getContract(this.chaincodeName);

    const close = () => {
      gateway.close();
      client.close();
    };

    return { contract, close };
  }
}
