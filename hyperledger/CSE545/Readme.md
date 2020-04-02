# Dependencies for Hyperledger:
- Docker
- Docker Compose
- java-1.8
- Maven
- Gradle
- curl

# Steps to Follow to setup Hyperledger:
- cd hyperledger/CSE545/
- Run the following command: curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.0.1 1.4.6 0.4.18
- Build the maven project using: mvn clean 
- cp target/<jar name> ./
- Run the script: ./startFabric.sh
- mvn 
