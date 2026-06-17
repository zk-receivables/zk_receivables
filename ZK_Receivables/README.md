# ZK Receivables

## Introduction

ZK Receivables is a prototype of an information system that allows the confirmation of an entity's receivables balances by an auditor or an external party. This is achieved by employing Zero Knowledge Proofs, a permissionless blockchain, and smart contracts.  

This repository implements the Cryptographic Accounting System protocol developed in the paper: 

Can Cryptographic Accounting Systems Provide Audit Evidence?
By xxxx, xxxx and xxxx

The software consists of three parts. The first is a smart contract that enables entities to store information about their debtors and commitments to those debtors on the blockchain (ZK_Receivables). The second smart contract allows debtors to upload commitments to entities (ZK_Debtors). Both of these contracts are written in the Solidity programming language (https://github.com/ethereum/solidity.) The third software component is a client program, written in Python that simulates the calculation and uploading to the blockchain of the commitments and proofs (deploy.py).

The Python client program simulates the use of the smart contract and tests it. This program uses Brownie (https://eth-brownie.readthedocs.io/en/stable/index.html) which is a Python-based development and testing framework for smart contracts which uses the Ethereum Virtual Machine. This framework is used both to construct and interact with the smart contracts and send transactions. Initially, the program uploads the bytecode of the compiled smart contracts to the blockchain. The contracts’ addresses are returned, and the program then calls the constructor  of the ZK_Receivables contract to simulate the initialization of the smart contract by the entity. The debtors each initialize a smart contract (ZK_Debtors), upload their commitments, and send their contract addresses and the r they have used for their commitments to the relevant entities by a secure channel. The list of Ethereum addresses of the debtors are then uploaded by the entity to their smart contract, which uses a function modifier  to ensure only the owner can upload these addresses. The entity then computes the necessary commitments and uploads them, along with a set of zk-proofs to their smart contract. The verifier can then use the information in both the entities and the debtors smart contracts to verify the proofs. 

There are two support libraries pedersen_scheme.py and zk_snark.py, developed by the authors that provide standard cryptography services. 

For details of the protocol implemented in the code see sections 4.4 and 4.5 of the paper and Appendix 1 Protocols 2 and 3. All of the code is extensively commented and linked to the protocols in the paper. 

ALl of the code can be viewed on this repository without installing anything.

You can run the software as follows:

## Prerequisites

You must install https://www.docker.com on your system. This software allows ZK Receivables to run in a virtual machine on your system. This means GHG_EDL runs in its own container and does not affect the files on your system.

You may also need [git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/download/) if it is not already installed.

## Installation

Clone the repository to a local directory.
```
% git clone https://github.com/zk-receivables/zk_receivables 
```

Install [docker](https://www.docker.com/). This should include docker compose.

Make sure that docker desktop is running

In a terminal, make sure you are in the cloned directory. Issue the following command

```
% docker compose up -d
```

See Running ZK Receivables below for instructions on running the software.

When the application has terminated (type exit into the command line) you may need to press ctrl-c or issue the following command in another terminal

```
% docker compose down
```

## Running ZK Receivables

### Start docker compose

Make sure that docker desktop is running

In the cloned directory
```
% docker compose up -d
```
or 
```
% docker compose up --build
```
if the container needs to be rebuilt

then 
```
% docker compose exec sandbox bash
```
This command starts the ZK Receivables container and a command line. This command may have to be run in another terminal if the docker compose lines were run in the foreground.

You now be in the command line of the container with a unix virtual machine, the software, and all necessary packages. The software uses brownie as an interface to a test etherium blockchain. See https://eth-brownie.readthedocs.io/en/stable/quickstart.html for more information.

### To run ZK Receivables

```
% cd myprojects/ZK_Receivables
% brownie run scripts/deploy.py
```

These commands must be run inside the docker container - see above.

Brownie should start an etherium blockchain and execute the code in scripts/deploy.py which 

- Generates sample data for an entity and its debtors
- Deploys a smart contract (ZK_Debtor) for each debtor
- Calculates the debtors commitment and uploads it to the blockchain
- Communicates the r used for the commitment to the entity over a secure channel
- Deploys a smart contract for the entity (ZK_Receivables)
- Calculates the entities commitments and proofs and uploads to the blockchain
- (Auditor/Verifier) Downloads the entity commitments and proofs from the blockchain and 
    - verifies that the sum of the commitments for the entity's receivables can be unlocked with the entity's sum of r and v and the total balance of receivables.
    - verifies the ZK Proofs for each debtor
    - Verifies the binary ZK Prrof for d
- The program reports whether all the proofs are verified.

When you are finished with the container

```
% exit   #to exit the command line on the container
```
back in the local terminal
```
% docker compose down
```

# Making Changes

Changes should be made to the files in the cloned repository on your local machine. These changes are reflected in the docker contained as your directory is mapped into the contained by the docker files.

If you make any changes to the smart contracts (contracts/ZK_Debtors.sol, contracts/ZK_Receivables.sol). 

Then you must recompile the project

```
% brownie compile
```
in the ZK_Receivables directory.

If you make any changes to the deployment script.

Then you must rerun the project within brownie.

```
% brownie run scripts/deploy.py
```
in the ZK_Receivables directory.