// SPDX-License-Identifier: MIT1

// Solidity Contract to allows debtors to acknowledge their debts to various entities (suppliers) 
// on an ethereum blockchain.

// The contract is set up by an debtor that has an obligation to an entity.
// A commitment to the debtor is loaded onto the blockchain by the owner (debtor).

// Data in the smart contracts is encrypted using Pedersen Commitments (off-chain)
// and is used to verify the commitments off-chain without revealing the actual data
// by using zero-knowledge proofs (ZKPs) loaded onto the blockchain by the
// entity (supplier) that is owed the debt.

// Author for Review, Dec. 2024
// Licensed under MIT License

//contract definition

pragma solidity ^0.8.0;

contract ZK_Debtors {
    //structures definitions

    struct commitment {
        uint32 commitment_ID;
        uint256 commitment_x;
        bool commitment_y_odd;
        uint256 r;
    }

    // Data structure to store the description of the product or service
    struct description_struct {
        address owner;
        string owner_name;
        uint32 owner_ID;
    }

    // State variables - stored in the smart contract

    description_struct private description; // description of the product or service
    commitment[] private commitments; // array of commitments to an entity
    address public owner; // owner of the smart contract which is public

    // Constructor function
    // The owner of the smart contract is set to the address of the sender
    // The owner name and owner_ID are  initialized

    constructor() {
        owner = msg.sender;
        description.owner = owner; // owner of the smart contract i.e. entity that produces the product or service
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

    // Function to set the commitments to various entities (suppliers) - only the owner can use this function

    function set_commitment(
        uint16 _commitment_ID,
        uint256 _payable_commitment,
        bool _payable_commitment_y_odd
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can add commitments");
        // Check if the commitment ID already exists
        for (uint i = 0; i < commitments.length; i++) {
            require(
                commitments[i].commitment_ID != _commitment_ID,
                "Commitment ID already exists"
            );
        }
        // Add commitment to the array
        commitments.push(
            commitment({
                commitment_ID: _commitment_ID,
                commitment_x: _payable_commitment,
                commitment_y_odd: _payable_commitment_y_odd,
                r: 0
            })
        );
        return true;
    }

    // Function to get all the commitments to various entities (suppliers) - anybody can use this function
    // Anybody can use this function

    function get_commitments() public view returns (commitment[] memory) {
        return commitments;
    }
}
