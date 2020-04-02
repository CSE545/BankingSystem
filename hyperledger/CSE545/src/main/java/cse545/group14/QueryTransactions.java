package cse545.group14;

import org.hyperledger.fabric.gateway.Contract;
import org.hyperledger.fabric.gateway.Gateway;
import org.hyperledger.fabric.gateway.Network;
import org.hyperledger.fabric.gateway.Wallet;

import java.nio.file.Path;
import java.nio.file.Paths;

public class QueryTransactions {
    public static void main(String[] arr){
        try {
            // Load a file system based wallet for managing identities.
            Path walletPath = Paths.get("wallet");
            Wallet wallet = Wallet.createFileSystemWallet(walletPath);
            // load a CCP
            Path networkConfigPath = Paths.get("first-network", "connection-org1.yaml");

            Gateway.Builder builder = Gateway.createBuilder();
            builder.identity(wallet, "user1").networkConfig(networkConfigPath).discovery(true);
            // create a gateway connection
            try (Gateway gateway = builder.connect()) {
                // get the network and contract
                Network network = gateway.getNetwork("mychannel");
                Contract contract = network.getContract("BankTransactions");
                byte[] result;
                result = contract.evaluateTransaction("queryAll");
                System.out.println("The following Transactions are present in hyperledger:");
                System.out.println(new String(result));
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }
}
