# Dependencies for Hyperledger:
- Docker
- Docker Compose
- java-1.8
- Maven
- Gradle
- curl

# Steps to Follow to setup Hyperledger:
- cd hyperledger/CSE545/
- Run the following command: `curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.0.1 1.4.6 0.4.18`
- Build the maven project using: `mvn clean package assembly:single`
- cp target/group14-1.0.0-jar-with-dependencies.jar ./
- Run the script: ./startFabric.sh
- Enroll Admin: `java -cp group14-1.0.0-jar-with-dependencies.jar cse545.group14.EnrollAdmin`
- Register User: `java -cp group14-1.0.0-jar-with-dependencies.jar cse545.group14.RegisterUser`
- In order to Query the transactions present in hyperledger, run `java -cp group14-1.0.0-jar-with-dependencies.jar cse545.group14.QueryTransactions`
- Run the service to Insert Transactions: `java -cp group14-1.0.0-jar-with-dependencies.jar cse545.group14.InsertTransactions`
