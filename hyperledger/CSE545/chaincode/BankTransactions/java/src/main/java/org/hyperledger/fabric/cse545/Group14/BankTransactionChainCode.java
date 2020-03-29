package org.hyperledger.fabric.cse545.Group14;
import java.util.ArrayList;
import java.util.List;
import org.hyperledger.fabric.contract.Context;
import org.hyperledger.fabric.contract.ContractInterface;
import org.hyperledger.fabric.contract.annotation.Contract;
import org.hyperledger.fabric.contract.annotation.Default;
import org.hyperledger.fabric.contract.annotation.Info;
import org.hyperledger.fabric.contract.annotation.Transaction;
import org.hyperledger.fabric.shim.ChaincodeException;
import org.hyperledger.fabric.shim.ChaincodeStub;
import org.hyperledger.fabric.shim.ledger.KeyValue;
import org.hyperledger.fabric.shim.ledger.QueryResultsIterator;

import com.owlike.genson.Genson;

@Contract(
        name = "BankTransactions",
        info = @Info(
                title = "Bank Transactions contract",
                description = "The Bank Transactions contract for approved transactions"))

@Default
public class BankTransactionChainCode implements ContractInterface {
    private final Genson genson = new Genson();

    @Transaction
    public BankTransactions queryBankTransactions(final Context ctx, final String key){
        ChaincodeStub chaincodeStub = ctx.getStub();
        String bankTransactionsState = chaincodeStub.getStringState(key);
        if (bankTransactionsState.isEmpty()) {
            String errorMessage = String.format("Car %s does not exist", key);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage);
        }
        BankTransactions bankTransactions = genson.deserialize(bankTransactionsState, BankTransactions.class);
        return bankTransactions;
    }

    @Transaction()
    public BankTransactions[] queryAll(final Context ctx) {
        ChaincodeStub chaincodeStub = ctx.getStub();
        final String startKey = "0";
        final String endKey = "10000000";
        List<BankTransactions> bankTransactionsList = new ArrayList<BankTransactions>();
        QueryResultsIterator<KeyValue> results = chaincodeStub.getStateByRange(startKey, endKey);
        for (KeyValue result: results) {
            BankTransactions bankTransactions = genson.deserialize(result.getStringValue(), BankTransactions.class);
            bankTransactionsList.add(bankTransactions);
        }
        BankTransactions[] response = bankTransactionsList.toArray(new BankTransactions[bankTransactionsList.size()]);
        return response;
    }

    @Transaction()
    public BankTransactions createBankTransactions(final Context ctx, final String key, final String request_id,
                                                   final String amount, final String from_account,
                                                   final String to_account) {
        ChaincodeStub chaincodeStub = ctx.getStub();
        String bankTransactionsState = chaincodeStub.getStringState(key);
        if (!bankTransactionsState.isEmpty()) {
            String errorMessage = String.format("Transaction %s already exists", key);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage);
        }

        BankTransactions bankTransaction = new BankTransactions(request_id, amount, from_account, to_account);
        bankTransactionsState = genson.serialize(bankTransaction);
        chaincodeStub.putStringState(key, bankTransactionsState);

        return bankTransaction;
    }

    @Transaction()
    public void initLedger(final Context ctx) {
        ChaincodeStub chaincodeStub = ctx.getStub();

        String[] sampleData = {
                "{ \"request_id\": \"0\", \"amount\": \"0\", \"from_account\": \"0\", \"to_account\": \"0\" }"
        };

        for (int i = 0; i < sampleData.length; i++) {
            String key = String.format("%d", i);

            BankTransactions data = genson.deserialize(sampleData[i], BankTransactions.class);
            String bankTransactionState = genson.serialize(data);
            chaincodeStub.putStringState(key, bankTransactionState);
        }
    }
}