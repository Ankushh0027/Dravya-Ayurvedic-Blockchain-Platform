#!/bin/bash
set -e

# Constants
FABRIC_VERSION="2.5.9"
CA_VERSION="1.5.12"
CHANNEL_NAME="dravya-channel"
CHAINCODE_NAME="traceability"
CHAINCODE_LANG="typescript"
CHAINCODE_PATH="../../chaincode"

cd "$(dirname "$0")/.."

echo "=========================================================="
echo "Starting Dravya Hyperledger Fabric Development Network"
echo "=========================================================="

if [ ! -d "fabric-samples" ]; then
    echo "Downloading fabric-samples and binaries (Fabric v$FABRIC_VERSION, CA v$CA_VERSION)..."
    curl -vsS https://raw.githubusercontent.com/hyperledger/fabric/master/scripts/bootstrap.sh | bash -s -- $FABRIC_VERSION $CA_VERSION
fi

cd fabric-samples/test-network

echo "Bringing down any existing network..."
./network.sh down

echo "Starting network with CAs (Org1, Org2)..."
./network.sh up createChannel -c $CHANNEL_NAME -ca

echo "Adding Org3 to the network..."
pushd addOrg3
./addOrg3.sh up -c $CHANNEL_NAME -ca
popd

echo "Deploying chaincode for 3 Orgs..."
# We must install dependencies in chaincode before deployment
echo "Installing chaincode dependencies..."
pushd $CHAINCODE_PATH
npm install
npm run build
rm -rf node_modules
popd

# Export Fabric binaries path
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/

# Use our custom 3Org script with 3-org AND policy
../../scripts/deployCCAAS3Orgs.sh $CHANNEL_NAME $CHAINCODE_NAME $CHAINCODE_PATH true 1.0 1 "NA" "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')" "NA" 3 5 false

echo "=========================================================="
echo "Network started and chaincode deployed!"
echo "Org1 (Govt Authority), Org2 (Laboratory), and Org3 (Dravya Platform) are ready."
echo "=========================================================="
