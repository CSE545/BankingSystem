package org.hyperledger.fabric.cse545.Group14;
import java.util.Objects;
import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;
import com.owlike.genson.annotation.JsonProperty;

@DataType()
public final class BankTransactions {

    @Property()
    private final String request_id;

    @Property()
    private final String from_account;

    @Property()
    private final String to_account;

    @Property()
    private final String amount;

    @Property()
    private final String transfer_type;

    public String getRequest_id() {
        return request_id;
    }

    public String getFrom_account() {
        return from_account;
    }

    public String getTo_account() {
        return to_account;
    }

    public String getAmount() {
        return amount;
    }

    public String getTransfer_type() { return transfer_type; }

    public BankTransactions(@JsonProperty("request_id") final String request_id,
                            @JsonProperty("amount") final String amount,
                            @JsonProperty("from_account") final String from_account,
                            @JsonProperty("to_account") final String to_account,
                            @JsonProperty("transfer_type") final String transfer_type){
        this.request_id = request_id;
        this.from_account = from_account;
        this.to_account = to_account;
        this.amount = amount;
        this.transfer_type = transfer_type;
    }

    @Override
    public boolean equals(final Object obj) {
        if (this == obj) {
            return true;
        }

        if ((obj == null) || (getClass() != obj.getClass())) {
            return false;
        }

        BankTransactions other = (BankTransactions) obj;

        return Objects.deepEquals(new String[] {getRequest_id(), getAmount(), getFrom_account(), getTo_account(), getTransfer_type()},
                new String[] {other.getRequest_id(), other.getAmount(), other.getFrom_account(), other.getTo_account(), other.getTransfer_type()});
    }

    @Override
    public int hashCode() {
        return Objects.hash(getRequest_id(), getAmount(), getFrom_account(), getTo_account(), getTransfer_type());
    }

    @Override
    public String toString() {
        return this.getClass().getSimpleName() + "@" + Integer.toHexString(hashCode()) + " [request_id=" + request_id + ", amount="
                + amount + ", from_account=" + from_account + ", to_account=" + to_account + ", transfer_type=" + transfer_type + "]";
    }
}
