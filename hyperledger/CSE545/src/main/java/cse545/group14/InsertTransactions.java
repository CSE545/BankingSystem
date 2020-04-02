package cse545.group14;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;

import org.hyperledger.fabric.gateway.Contract;
import org.hyperledger.fabric.gateway.Gateway;
import org.hyperledger.fabric.gateway.Network;
import org.hyperledger.fabric.gateway.Wallet;

public class InsertTransactions {
    static {
        System.setProperty("org.hyperledger.fabric.sdk.service_discovery.as_localhost", "true");
    }
    public static void main(String[] args) throws Exception {
        try {
            String myDriver = "com.mysql.cj.jdbc.Driver";
            String url = "jdbc:mysql://localhost:3306/ss_project";
            String username = "root";
            String password = "root";
            String hyperledger_id = "0";
            String[] transaction_tables = {"transaction_management_transaction","transaction_management_fundtransfers","transaction_management_cashiercheck"};
            String[] to_account_column = {"to_account_id", "to_account_id", "pay_to_the_order_of"};
            Class.forName(myDriver);
            java.sql.Connection conn = DriverManager.getConnection(url, username, password);
            Statement st = conn.createStatement();;

            try {
                while (true){
                    String state_query = "Select last_hyperledger_id from transaction_management_hyperledgerstate limit 1";
                    ResultSet resultSet_state_query = st.executeQuery(state_query);
                    if (resultSet_state_query!=null && resultSet_state_query.next() == false) {
                        // Injesting first time into hyperledger
                        String insertQuery = "INSERT INTO transaction_management_hyperledgerstate " +
                                "VALUES (1, \"0\")";
                        st.executeUpdate(insertQuery);
                    } else if(resultSet_state_query!=null){
                        while (resultSet_state_query.next()) {
                            hyperledger_id = resultSet_state_query.getString(1);
                        }
                    }
                    Path walletPath = Paths.get("wallet");
                    Wallet wallet = Wallet.createFileSystemWallet(walletPath);
                    // load a CCP
                    Path networkConfigPath = Paths.get("first-network", "connection-org1.yaml");
                    Gateway.Builder builder = Gateway.createBuilder();
                    builder.identity(wallet, "user1").networkConfig(networkConfigPath).discovery(true);
                    int i = 0;
                    for (String transaction_table : transaction_tables) {
                        String transaction_query = "SELECT request_id, amount, from_account_id, " + to_account_column[i] + ", transfer_type " +
                                "FROM  " + transaction_table + " WHERE status=\"APPROVED\" AND hyperledger_id IS NULL";
                        ResultSet rs = st.executeQuery(transaction_query);
                        HashMap<String,String> hm=new HashMap<String,String>();
                        if (rs != null) {
                            try (Gateway gateway = builder.connect()) {
                                  Network network = gateway.getNetwork("mychannel");
                                  Contract contract = network.getContract("BankTransactions");
                            while (rs.next()) {
                                hyperledger_id = Integer.toString(Integer.parseInt(hyperledger_id) + 1);
                                contract.submitTransaction("createBankTransactions", hyperledger_id, rs.getString(1),
                                        rs.getString(2), rs.getString(3), rs.getString(4), rs.getString(5));

                                hm.put(rs.getString(1),hyperledger_id);
                            }
                            for(Map.Entry m:hm.entrySet())
                            {
                                String updateHyperledgerIdQuery = "UPDATE " + transaction_table + " SET hyperledger_id=\""
                                        + m.getValue() + "\" WHERE request_id=" + m.getKey();
                                st.executeUpdate(updateHyperledgerIdQuery);

                            }
                            String updateHyperledgerStateQuery = "UPDATE transaction_management_hyperledgerstate " +
                                    "SET last_hyperledger_id = \"" + hyperledger_id + "\" " +
                                    "WHERE id=1";
                            st.executeUpdate(updateHyperledgerStateQuery);
                        }
                        i += 1;
                    }
                    }
                    try (Gateway gateway = builder.connect()) {
                        Network network = gateway.getNetwork("mychannel");
                        Contract contract = network.getContract("BankTransactions");
                        byte[] result;
                        result = contract.evaluateTransaction("queryAll");
                        System.out.println("The following Transactions are present in hyperledger:");
                        System.out.println(new String(result));
                    }
            }} catch (Exception ex) {
                ex.printStackTrace();
            } finally {
                if (st != null) {
                    st.close();
                }
                if (conn != null) {
                    conn.close();
                }
            }
        }catch (Exception ex) {
            ex.printStackTrace();
        }
    }

}
