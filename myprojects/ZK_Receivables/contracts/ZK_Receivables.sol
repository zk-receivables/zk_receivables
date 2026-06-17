// SPDX-License-Identifier: MIT1

// Solidity Contract to allows entities to confirm their receivables to various debtors 
// on an ethereum blockchain.

// The contract is set up by an entity that has an obligations from various debtors.
// A commitment to the balance with the debtor is loaded onto the blockchain by the owner (entity).

// Data in the smart contracts is encrypted using Pedersen Commitments (off-chain)
// and is used to verify the total balance of receivables off-chain without revealing the actual data
// by using zero-knowledge proofs (ZKPs) loaded onto the blockchain in this contract by the
// entity (supplier) that is owed the debt.

// Author for Review, Dec. 2024
// Licensed under MIT License

//contract definition

pragma solidity ^0.8.0;

contract ZK_Receivables {
    //structures definitions

    // structure to store the commitment information for a receivable
    struct commitment {
        uint256 commitment_x;
        bool commitment_y_odd;
    }

    // structure to hold the ZK_proofs for a receivable;
    struct ZK_proofs {
        uint32 receivable_ID;
        address debtor_contract_address;
        commitment c1;
        commitment c2;
        commitment c3;
        commitment T1;
        commitment T2;
        commitment T3;
        commitment T4;
        commitment hvik; // commitment to h^vik value for the proof
        uint256 s1;
        uint256 s2;
        uint256 s3;
        uint256 s4;
        uint256 s5;
        uint256 s6;
        uint256 k;
    }

    struct ZK_binary_proof {
        uint32 receivable_ID;
        address debtor_contract_address;
        commitment l;
        commitment a0;
        commitment a1;
        uint256 k;
        uint256 c1;
        uint256 r0;
        uint256 r1;
    }

    // structure to hold the total of the commitments for an entity
    // and the total of the random factors used to generate the commitments for the entity
    struct total_commitments {
        commitment total_commitment; // total commitment for the entity
        uint256 total_random_factor; // total of the random factors used to generate the commitments for the entity
        uint32 total_receivables; // total of receivables for the entity
    }

    // Data structure to store the description of the entity
    struct description_struct {
        address owner;
        string owner_name;
        uint32 owner_ID;
    }

    // State variables - stored in the smart contract

    description_struct private description; // description of the entity that owes the receivables
    ZK_proofs[] private ZK_receivables; // array of receivables for the entity
    ZK_binary_proof[] private ZK_binary_receivables; // array of binary proofs for receivables for the entity
    total_commitments private total_commitments_entity; // total commitments for the entity
    address public owner; // owner (entity) of the smart contract which is public

    // Constructor function
    // The owner of the smart contract is set to the address of the sender
    // The owner name and owner_ID are  initialized

    constructor() {
        owner = msg.sender;
        description.owner = owner; // owner of the smart contract i.e. entity that is confirming receivables
        // initialize the description
        description.owner_name = "";
        description.owner_ID = 0;
    }

    //functions

    // Function that the owner can use to set the description of contract

    function set_description(
        string memory _owner_name,
        uint32 _owner_ID
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can set the description");
        description.owner_name = _owner_name;
        description.owner_ID = _owner_ID;
        return true;
    }

    // Function to get the description of the contract - anybody can use this function

    function get_description()
        public
        view
        returns (
            address, // owner
            string memory, // owner_name
            uint32 // owner_ID
        )
    {
        return (
            description.owner,
            description.owner_name,
            description.owner_ID
        );
    }

    // Function to set the commitments to various receivables (customers) - only the owner can use this function

    function set_ZK_receivable(
        ZK_proofs memory _ZK_proof
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can add commitments");
        // Add commitment to the array
        ZK_receivables.push(
            ZK_proofs({
                receivable_ID: _ZK_proof.receivable_ID,
                debtor_contract_address: _ZK_proof.debtor_contract_address,
                c1: commitment({
                    commitment_x: _ZK_proof.c1.commitment_x,
                    commitment_y_odd: _ZK_proof.c1.commitment_y_odd
                }),
                c2: commitment({
                    commitment_x: _ZK_proof.c2.commitment_x,
                    commitment_y_odd: _ZK_proof.c2.commitment_y_odd
                }),
                c3: commitment({
                    commitment_x: _ZK_proof.c3.commitment_x,
                    commitment_y_odd: _ZK_proof.c3.commitment_y_odd
                }),
                T1: commitment({
                    commitment_x: _ZK_proof.T1.commitment_x,
                    commitment_y_odd: _ZK_proof.T1.commitment_y_odd
                }),
                T2: commitment({
                    commitment_x: _ZK_proof.T2.commitment_x,
                    commitment_y_odd: _ZK_proof.T2.commitment_y_odd
                }),
                T3: commitment({
                    commitment_x: _ZK_proof.T3.commitment_x,
                    commitment_y_odd: _ZK_proof.T3.commitment_y_odd
                }),
                T4: commitment({
                    commitment_x: _ZK_proof.T4.commitment_x,
                    commitment_y_odd: _ZK_proof.T4.commitment_y_odd
                }),
                hvik: commitment({
                    commitment_x: _ZK_proof.hvik.commitment_x,
                    commitment_y_odd: _ZK_proof.hvik.commitment_y_odd
                }),
                s1: _ZK_proof.s1,
                s2: _ZK_proof.s2,
                s3: _ZK_proof.s3,
                s4: _ZK_proof.s4,
                s5: _ZK_proof.s5,
                s6: _ZK_proof.s6,
                k: _ZK_proof.k
            })
        );
        return true;
    }

    function set_ZK_receivable_binary(
        ZK_binary_proof memory _ZK_b_proof
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can add commitments");
        // Add commitment to the array
        ZK_binary_receivables.push(
            ZK_binary_proof({
                receivable_ID: _ZK_b_proof.receivable_ID,
                debtor_contract_address: _ZK_b_proof.debtor_contract_address,
                l: commitment({
                    commitment_x: _ZK_b_proof.l.commitment_x,
                    commitment_y_odd: _ZK_b_proof.l.commitment_y_odd
                }),
                a0: commitment({
                    commitment_x: _ZK_b_proof.a0.commitment_x,
                    commitment_y_odd: _ZK_b_proof.a0.commitment_y_odd
                }),
                a1: commitment({
                    commitment_x: _ZK_b_proof.a1.commitment_x,
                    commitment_y_odd: _ZK_b_proof.a1.commitment_y_odd
                }),
                k: _ZK_b_proof.k,
                c1: _ZK_b_proof.c1,
                r0: _ZK_b_proof.r0,
                r1: _ZK_b_proof.r1
            })
        );
        return true;
    }

    function set_total_commitments(
        commitment memory _total_commitments,
        uint256 _total_random_factor,
        uint32 _total_receivables
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can add commitments");
        // Set total commitment
        total_commitments_entity.total_commitment = commitment({
            commitment_x: _total_commitments.commitment_x,
            commitment_y_odd: _total_commitments.commitment_y_odd
        });
        total_commitments_entity.total_random_factor = _total_random_factor;
        total_commitments_entity.total_receivables = _total_receivables;

        return true;
    }

    // Function to get all the commitments to various receivables (customers) - anybody can use this function
    // Anybody can use this function

    function get_ZK_receivables() public view returns (ZK_proofs[] memory) {
        return ZK_receivables;
    }

    function get_ZK_binary_receivables()
        public
        view
        returns (ZK_binary_proof[] memory)
    {
        return ZK_binary_receivables;
    }

    function get_total_commitments()
        public
        view
        returns (total_commitments memory)
    {
        return total_commitments_entity;
    }
}
