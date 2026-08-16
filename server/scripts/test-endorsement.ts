import { FabricConnectionService } from '../src/services/fabric-connection.service';
import { Role } from '@prisma/client';

async function main() {
    console.log("Connecting to Fabric using ADMIN (Org3) identity...");
    const { contract, close } = await FabricConnectionService.getContractForRole(Role.ADMIN);
    
    try {
        console.log("Attempting to invoke CreateTraceabilityRecord...");
        // Generate random ID
        const recordId = "test_record_" + Date.now();
        await contract.submitTransaction(
            'CreateTraceabilityRecord',
            recordId,
            'TEST_BATCH',
            'dummy_hash',
            '1',
            'Org3MSP',
            new Date().toISOString()
        );
        console.log("Transaction succeeded! (Wait, this shouldn't happen if a peer is down)");
    } catch (e: any) {
        console.error("\n--- TRANSACTION FAILED (AS EXPECTED) ---");
        console.error("Error Message: ", e.message);
        console.error("----------------------------------------\n");
    } finally {
        close();
    }
}

main().catch(console.error);
