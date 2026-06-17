#!/usr/bin/python3

# Deployment script for 
# Creating simulated data for debtors and receivables
# Deployment of ZK_Receivables and ZK_Debtors contracts
# Verification of commitments and ZK proofs for the receivables of one entity

# Author: **** *******
# Date: 2024-06-10
# License: MIT License

import random
import sys
import copy

# add scripts dir to path to allow zk_snark.py and pedersen_scheme.py to be imported
sys.path.append("/code/myprojects/ZK_Receivables/scripts")

from brownie.network.contract import ProjectContract  # type: ignore
from brownie import ZK_Receivables, ZK_Debtors, accounts
import tinyec.ec as tiny
import tinyec.registry as reg
from pedersen_scheme import Ped_scheme
from zk_snark import ZkBinarySnark

random.seed(
    1234567890
)  # set seed for reproducibility - randomness is not secure - use secrets library for better randomness

de_bug = False  # Set to True to enable debug prints, False to disable
verbose = True  # Set to True to enable verbose prints, False to disable

ped_scheme = Ped_scheme()  # Initialize the Pedersen scheme instance
zk_snark = ZkBinarySnark()  # Initialize the ZK Binary SNARK instance


def generate_sample_data(no_of_debtors, no_of_receivables, no_of_anonymity_sample):
    """
    Generate sample data for the debtors and receivables.
    Args:
        no_of_debtors (int): The number of debtors to generate.
        no_of_receivables (int): The number of receivables to select from the anonymity sample.
        no_of_anonymity_sample (int): The number of receivables to include in the anonymity sample.
    Returns:
        dict: A dictionary containing the generated debtors
        dict: A dictionary containing the sample receivables.
                (balance = 0 for the non-selected receivables in the anonymity sample)
    """

    # Generate sample data for the debtors and receivables
    print("Generating sample data for debtors and receivables...")
    # Code to generate sample data for the debtors and receivables
    debtors = {}
    for i in range(no_of_debtors):
        # Generate balances for each debtor
        balance = random.randint(1000, 100000)  # Example balance for each debtor
        debtor_account = (
            accounts.add()
        )  # Create a new account for each debtor using Brownie
        debtors[i + 1] = {
            "Balance": balance,  # Store the balance for each debtor
            "Account": debtor_account,  # Assign the created account to each debtor
        }  # Store debtor information in a dictionary

    if de_bug:
        print(debtors[3])  # Print the information for debtor 2 as an example

    sample_receivables_ids = random.sample(
        debtors.keys(), no_of_anonymity_sample
    )  # Randomly select sample ofreceivables from the debtors

    receivables_ids = random.sample(
        sample_receivables_ids, no_of_receivables
    )  # Randomly select receivables from the selected anonymity sample

    if de_bug:
        print(
            sample_receivables_ids
        )  # Print the selected anonymity sample of receivables
        print(receivables_ids)  # Print the selected receivables

    sample_receivables = {}
    for receivable_id in sample_receivables_ids:
        debtor_account = debtors[receivable_id][
            "Account"
        ]  # Get the account for the receivable from the debtors dictionary
        debtor_balance = debtors[receivable_id][
            "Balance"
        ]  # Get the balance for the receivable from the debtors dictionary

        if receivable_id in receivables_ids:
            sample_receivables[receivable_id] = {
                "Balance": debtor_balance,  # Set the balance for the selected receivables in the anonymity sample to the corresponding balance from the debtors dictionary
                "Account": debtor_account,  # Set the account for the selected receivables in the anonymity sample to the corresponding account from the debtors dictionary
            }
        else:
            sample_receivables[receivable_id] = {
                "Balance": 0,
                "Debtor_Account": debtor_account,
            }  # Set the balance to 0 for the non-selected receivables in the anonymity sample

    if de_bug:
        print(sample_receivables)  # Print the dictionary of the selected receivables

    # summarize the total balance of the selected receivables
    total_balance = sum(
        sample_receivables[receivable_id]["Balance"]
        for receivable_id in receivables_ids
    )
    count_all = len(sample_receivables)

    count_receivables_with_balance = sum(
        1
        for receivable_id in sample_receivables_ids
        if sample_receivables[receivable_id]["Balance"] > 0
    )

    if verbose:
        print(f"Total balance of the selected receivables: {total_balance}")
        print(f"Number of selected receivables: {count_all}")
        print(
            f"Number of selected receivables with balance: {count_receivables_with_balance}"
        )

    return debtors, sample_receivables


def deploy_ZK_Debtors(debtors):
    """
    Deploy the ZK_Debtors contract for each debtor and store the contract address in a dictionary.

    Args:        debtors (dict): A dictionary containing the information about the debtors, including their balances and accounts.
    Returns:     debtors (dict): A dictionary containing the updated information about the debtors, 
                                    including the address of the deployed ZK_Debtors contract for each debtor.
    """
    # Deploy the ZK_Debtors contract for each debtor
    print("Deploying ZK_Debtors contracts for each debtor...")
    # Code to deploy ZK_Debtors contracts for each debtor
    for debtor_id, debtor_info in debtors.items():
        account = debtor_info["Account"]  # Get the account for the debtor
        zk_debtor_contract = ZK_Debtors.deploy(
            {"from": account}
        )  # Deploy the ZK_Debtors contract for the debtor
        debtors[debtor_id][
            "Contract"
        ] = zk_debtor_contract  # Store the address of the deployed contract in a dictionary
        if de_bug:
            print(
                f"ZK_Debtors contract deployed for debtor {debtor_id} at address: {zk_debtor_contract.address}"
            )
            print(
                debtors[1]
            )  # Print the information for the first debtor as an example
    return debtors


def upload_commitments(debtors_contracts):
    """
    Calculates and uploads the commitments for each debtor to the ZK_Debtors contract.

    Args:        debtors_contracts (dict): A dictionary containing the information about the debtors,
                                             including their balances, accounts and contract addresses.
    Returns:     debtors_contracts (dict): A dictionary containing the updated 
                                            information about the debtors, including the commitments for each debtor.

    """
    # Upload the commitments for each debtor to the ZK_Debtors contract
    print("Uploading commitments for each debtor to the ZK_Debtors contracts...")
    # Code to upload the commitments for each debtor to the ZK_Debtors contract

    # For each debtor Calculate and upload the commitments for each debtor to the ZK_Debtors contract
    for debtor_id, debtor_info in debtors_contracts.items():
        account = debtor_info["Account"]  # Get the account for the debtor
        balance = debtor_info["Balance"]  # Get the balance for the debtor
        contract = debtor_info["Contract"]  # Get the deployed contract address for the debtor

        r = ped_scheme.randn()  # Generate randomness for the commitment
        # add r to debtors dictionary for later use in generating ZK proofs
        debtors_contracts[debtor_id]["r"] = r

        # Calculate the commitment for the balance using the Pedersen scheme and compress it using the ZK Binary SNARK
        commitment = zk_snark.compress_point(
            ped_scheme.commit(balance, r)
        )  # Generate the commitment for the balance in compressed form using the Pedersen scheme and the ZK Binary SNARK

        commitment_id = 1  # Example commitment ID, can be modified to use unique IDs for each commitment if needed

        debtors_contracts[debtor_id][
            "commitment"
        ] = commitment  # Store the commitment in the debtors dictionary for later use in generating ZK proofs

        # Upload the commitment to the ZK_Debtors contract for the debtor
        transaction1 = contract.set_commitment(
            commitment_id,  # Commitment ID (can be used to identify different commitments for the same debtor if needed)
            commitment[0],  # Total payables commitment x value
            commitment[1],  # Total payables commitment even or odd
            {"from": account},
        )
        transaction1.wait(1)

    if verbose:
        print(
            f"Commitments uploaded for debtors with balance.\n"
        )  # Print the details of the commitment upload for each debtor

    return debtors_contracts  # Return the updated debtors dictionary with the commitments for each debtor
    


def communicate_r_to_entity(debtors_contracts, sample_receivables):
    """
    Communicate the randomness r for the commitments from the debtors to the entity for generating ZK proofs.
    args:
        debtors_contracts (dict): A dictionary containing the information about the debtors
        sample_receivables (dict): A dictionary containing the information about the selected receivables, including their balances and accounts.
    Returns:
        sample_receivables (dict): A dictionary containing the updated information about the selected receivables
                                    , including the communicated randomness r for the commitments from the 
                                    debtors to the entity for generating ZK proofs.
    """
    # Communicate the randomness r for the commitments from the debtors to the entity for generating ZK proofs
    print(
        "Communicating randomness r for the commitments from the debtors to the entity...\n"
    )
    # Communicate the randomness r for the commitments from the debtors to the entity for generating ZK proofs
    for receivables_id, receivables_info in sample_receivables.items():

        if sample_receivables[receivables_id]["Balance"] > 0:
            r = debtors_contracts[receivables_id][
                "r"
            ]  # Get the randomness r for the debtor's commitment
            print(
                f"Communicating randomness r for receivable {receivables_id} from debtor to entity: {r}"
            )  # Print the details of the communication of randomness r from the
            sample_receivables[receivables_id]["r"] = r
            # Store the randomness r for the commitment in the sample_receivables dictionary for later use in generating ZK proofs

    if verbose:
        print(
            f"Randomness r communicated from debtors to entity for generating ZK proofs.\n"
        )  # Print the details of the communication of randomness r from the debtors to the entity
    if de_bug:
        print(
            sample_receivables
        )  # Print the updated sample_receivables dictionary with the communicated randomness r for verification
    
    return sample_receivables # Return the updated sample_receivables dictionary with the communicated randomness r for the commitments from the debtors to the entity for generating ZK proofs


def deploy_ZK_Receivables():
    """
    Deploy the ZK_Receivables contract for the entity and return the contract address.
    Returns:
        entity_contract (dict): A dictionary containing the information about the deployed ZK_Receivables contract 
                                for the entity.
    """
    # Deploy the ZK_Receivables contract for the entity
    print("Deploying ZK_Receivables contract for the entity... \n")

    # Deploy the ZK_Receivables contract for the entity
    entity_contract = (
        {}
    )  # Create a dictionary to store the information about the entity contract

    receivable_account = (
        accounts.add()
    )  # Create a new account for the entity using Brownie
    # Store the account for the entity in a variable for later use
    entity_contract["Account"] = (
        receivable_account  # Store the account for the entity in a variable for later use
    )
    # Deploy the ZK_Receivables contract for the entity and store the contract address in the entity_contract dictionary
    entity_contract["Contract"] = ZK_Receivables.deploy(
        {"from": receivable_account}
    )  # Deploy the ZK_Receivables contract for the entity
    
    if verbose:
        print(
            f"ZK_Receivables contract deployed for the entity at address: {entity_contract['Contract'].address}\n"
        )  # Print the details of the deployed ZK_Receivables contract for the entity
    
    return entity_contract


def generate_ZK_proof(sample_receivables, debtors_contracts):
    """
    Generate the ZK proof for the entity's receivables using the ZK Binary SNARK and the information about the commitments and randomness for the receivables.
    Args:
        sample_receivables (dict): A dictionary containing the information about the receivables for which to generate ZK proofs.
        debtors_contracts (dict): A dictionary containing the information about the debtors' contracts.
    Returns:
        receivable_proofs (dict): A dictionary containing the generated ZK proofs for each receivable.
        binary_proof_d (dict): A dictionary containing the generated binary proofs for d[i] for each receivable.
        total_proof (dict): A dictionary containing the generated ZK proof for the total balance commitment for the entity's receivables.
    """
    # Generate the ZK proof for the entity's receivables
    print("Generating ZK proof for the entity's receivables...\n")
    
    # Generate the commitments and ZK proofs for the entity's receivables using Protocol 2 in the Appendix to the paper 
    # Generate the commitments and ZK binary proofs for the entity's receivables using Protocol 3 in the Appendix to the paper 
    # Aggregate the entity's receivables commitments and v+r values to generate the proof for the total balance commitment for the entity's receivables using Protocol 4 in the Appendix to the paper
    
    # Create dictionaries to store the commitments and ZK proofs for the entity's receivables
    receivable_proofs = (
        {}
    )  # Create a dictionary to store the generated ZK proofs for each receivable
    total_proof = (
        {}
    )  # Create a dictionary to store the generated ZK proof for the total balance commitment for the entity's receivables
    binary_proof_d = (
        {}
    )  # Create a dictionary to store the generated binary proof for d[i] for each receivable

    # Initialize variables to store the sum of the commitments and randomness for the receivables in the anonymity sample for later use in generating ZK proofs for the entity's total balance commitment
    sum_r_v = 0  # Initialize a variable to store the sum of the randomness r for the commitments for the receivables in the anonymity sample for later use in generating ZK proofs
    sum_c1 = None  # Initialize a variable to store the sum of the commitments c1 for the receivables in the anonymity sample for later use in generating ZK proofs
    sum_bal = 0  # Initialize a variable to store the sum of the balances for the receivables in the anonymity sample for later use in generating ZK proofs

    # Retrieve the necessary information for generating the ZK proof for one receivable from the sample_receivables dictionary
    for receivables_id, receivables_info in sample_receivables.items():
        receivable_contract = debtors_contracts[receivables_id][
            "Contract"
        ].address  # Get the contract for the receivable from the debtors_contracts dictionary
        balance = receivables_info[
            "Balance"
        ]  # Get the balance for the receivable from the sample_receivables dictionary

        # Generate commitment to te receivable's balance

        if balance > 0:

            r = receivables_info[
                "r"
            ]  # Get the randomness r for the commitment from the sample_receivables dictionary
            d = 1  # Set the entity obligation indicator to 1 for the selected receivables in the anonymity sample
        else:
            r = 0  # Set r to 0 for the non-selected receivables in the anonymity sample since we do not know r.
            d = 0  # Set the entity obligation indicator to 0 for the non-selected receivables in the anonymity sample

        v = (
            ped_scheme.randn()
        )  # Generate randomness for the commitment to ensure it is different from the debtor's commitment and does not reveal any information about the balance
        # Save the randomness v for the commitment in the sample_receivables dictionary for later use in generating ZK proofs
        sample_receivables[receivables_id]["v"] = v

        sum_bal += balance  # Calculate the sum of the balances for the receivables in the anonymity sample to use in generating ZK proofs for the entity's total balance commitment

        r_v = (r + v) % ped_scheme.n  # Calculate the sum of r and v for the commitment

        # Step 5: Sum the randomness r+v for the commitments for the receivables in the anonymity sample to use in generating ZK proofs for the entity's total balance commitment
        sum_r_v = (r_v + sum_r_v) % ped_scheme.n
        # Calculate the sum of r+v for the commitments for the receivables in the anonymity sample to use in generating ZK proofs for the entity's total balance commitment

        c1 = ped_scheme.commit(
            balance, r_v
        )  # Step 4:Generate the commitment for the balance using the Pedersen scheme

        # Step 5:Sum the commitments c1 for the receivables in the anonymity sample to use in generating ZK proofs for the entity's total balance commitment
        if sum_c1 is not None:
            sum_c1 = sum_c1 + c1
        else:
            sum_c1 = c1  # Initialize sum_c1 with the first commitment if it is not already initialized

        # get the debtors commitment for the receivable from the debtors_contracts dictionary to use in the ZK proof generation
        delta = zk_snark.uncompress_point(
            debtors_contracts[receivables_id]["commitment"]
        )  # Get the commitment for the debtor from the debtors_contracts dictionary

        # Step 6: Entity commitments to r[i] * d[i], v[i] for ZK Proofs
        w = ped_scheme.randn()  # entity random value for commitment to r[i] * d[i]
        z = ped_scheme.randn()  # entity random value for commitment to v[i]
        c2 = ped_scheme.commit(
            r * d, w
        )  # Prover generates commitment c2 to r[i] x d[i]
        c3 = ped_scheme.commit(v, z)  # Prover generates commitment c3 to v[i]

        # Step 7: Commitment to the debtors commitment and to randomness for d[i] and bal[i] * d[i] (T1 and T2)is not standard

        t1 = ped_scheme.randn()  # random number for the commitment to d[i]
        T1 = delta * t1  # Commitment to randomness for d[i]

        t2 = ped_scheme.randn()  # random number for the commitment to bal[i] * d[i]
        t3 = ped_scheme.randn()  # random number for the commitment to v[i]
        T2 = ped_scheme.commit(t2, t3)  # Commitment to randomness for bal[i] * d[i]

        t4 = ped_scheme.randn()  # random number for the commitment to v[i]
        T3 = ped_scheme.commit(t3, t4)  # Commitment to randomness for v[i]

        t5 = ped_scheme.randn()  # random number for the commitment to v[i]
        t6 = ped_scheme.randn()  # random number for the commitment to v[i]
        T4 = ped_scheme.commit(t5, t6)  # Commitment to randomness for v[i]

        # Step 8: Generate challenge for ZK proof generation using Fiat-Shamir heuristic
        k = zk_snark.generate_challenge(
            c1, c2, c3, T1, T2, T3, T4
        )  # Prover generates challenge for ZK proof generation using Fiat-Shamir

        # Step 9: Generate the ZK proof for the receivable using the generated challenge and the commitments and randomness for the receivable
        
        # Generate proof for d[i]
        hvik = ped_scheme.H * (
            v * k
        )  # Calculate the value of h^vik for use in the proof generation for d[i]
        s1 = (d * k + t1) % ped_scheme.n

        # Generate proof for bal[i] * d[i]
        s2 = (balance * d * k + t2) % ped_scheme.n

        # Generate proof for r[i]*d[i]
        s3 = (r * d * k + t3) % ped_scheme.n

        # Generate proof for w[i]
        s4 = (w * k + t4) % ped_scheme.n

        # Generate proof for v[i]
        s5 = (v * k + t5) % ped_scheme.n

        # Generate proof for z[i]
        s6 = (z * k + t6) % ped_scheme.n

        # Package up proofs in a dictionary ready for uploading to the ZK_Receivables contract

        receivable_proofs[receivables_id] = {
            "c1": c1,
            "c2": c2,
            "c3": c3,
            "T1": T1,
            "T2": T2,
            "T3": T3,
            "T4": T4,
            "hvik": hvik,
            "s1": s1,
            "s2": s2,
            "s3": s3,
            "s4": s4,
            "s5": s5,
            "s6": s6,
            "k": k,
        }

        if verbose:
            print(
                f"ZK proof generated for receivable {receivables_id}.\n"
            )  

        # Protocol 3: Generate the binary commitments and ZK binary proofs for d[i] for the receivable 
        # using the ZK Binary SNARK

        commitments_d = zk_snark.generate_commitments(
            d
        )  # Generate the binary commitments for d[i] for the receivable using the ZK Binary SNARK
        challenge = zk_snark.generate_challenge(
            commitments_d["l"], commitments_d["a0"], commitments_d["a1"]
        )
        binary_proof_d[receivables_id] = zk_snark.prove(commitments_d, d, challenge)

        if verbose:
            print(
                f"Binary proof generated for d for receivable {receivables_id}.\n"
            )  # Print the details of the generated binary proof for d[i] for the receivable

    # end of loop over receivables in the anonymity sample
    
    # Store the value of d[i] for the receivable in the binary_proof dictionary for later use in generating ZK proofs for the entity's total balance commitment
    # Save the sum of r+v for the commitments for the receivables in the anonymity sample in the sample_receivables dictionary for later use in generating ZK proofs for the entity's total balance commitment
    total_proof["sum_r_v"] = sum_r_v
    total_proof["sum_c1"] = sum_c1
    total_proof["sum_bal"] = sum_bal

    total_rec_verified = ped_scheme.verify(
        sum_c1, sum_bal, sum_r_v
    )  # Verify the sum of the commitments c1 for the receivables in the anonymity sample using the Pedersen scheme with the sum of the balances and the sum of r+v for the commitments

    if verbose:
        print(
            f"Verification of the sum of the commitments c1 for the receivables in the anonymity sample: {total_rec_verified}\n"
        )  # Print the result of the verification of the sum of the commitments c1 for the receivables in the anonymity sample

    return receivable_proofs, binary_proof_d, total_proof


def verify_ZK_proof(proof, delta):
    """
    Verify the ZK proof for one receivable using the ZK Binary SNARK and the information about the commitments and randomness for the receivable.
    Args:
        proof (dict): A dictionary containing the generated ZK proof for one receivable.
        delta (tuple): The commitment for the debtor's receivable.
    Returns:
        bool: True if the ZK proof is verified successfully, False otherwise.
    """
    
    # Implementation for verifying ZK proofs

    # unpack proof for one receivable from the proofs dictionary
    c1 = proof["c1"]
    c2 = proof["c2"]
    c3 = proof["c3"]
    T1 = proof["T1"]
    T2 = proof["T2"]
    T3 = proof["T3"]
    T4 = proof["T4"]
    hvik = proof["hvik"]
    s1 = proof["s1"]
    s2 = proof["s2"]
    s3 = proof["s3"]
    s4 = proof["s4"]
    s5 = proof["s5"]
    s6 = proof["s6"]
    k = proof["k"]

    # Verify proof for d[i]
    lhs = delta * s1 + hvik
    rhs = c1 * k + T1
    is_verified_d = lhs == rhs
    if de_bug:
        print(f"Proof for d is verified: {is_verified_d}")

    # Verify proof for bal[i] * d[i]
    lhs = ped_scheme.commit(s2, s3) + hvik
    rhs = c1 * k + T2
    is_verified_bal_d = lhs == rhs
    if de_bug:
        print(f"Proof for bal * d is verified: {is_verified_bal_d}")

    # Verify proof for r[i]*d[i]
    lhs = ped_scheme.commit(s3, s4)
    rhs = c2 * k + T3
    is_verified_r_d = lhs == rhs

    if de_bug:
        print(f"Proof for r x d is verified: {is_verified_r_d}")

    # Verify proof for v[i]
    lhs = ped_scheme.commit(s5, s6)
    rhs = c3 * k + T4
    is_verified_v = lhs == rhs
    if de_bug:
        print(f"Proof for v is verified: {is_verified_v}\n")

    # Ensure all proofs are verified
    all_verified = all(
        [is_verified_d, is_verified_bal_d, is_verified_r_d, is_verified_v]
    )
    if de_bug:
        print(f"All ZK Receivables Proofs for Debtor are verified: {all_verified}\n")
    assert (
        all_verified == True
    ), f"ZK Receivables Proofs for Debtor  are not all verified"

    if de_bug:
        print(
            f"ZK proof for receivable  verified successfully.\n"
        )  # Print the details of the generated ZK proof for the receivable
        print(
            f"ZK proof for receivable: {proof}\n"
        )  # Print the generated ZK proof for the receivable
    return True  # Return True if all proofs are verified successfully


def upload_ZK_proofs(
    entity_contract, proofs, binary_proof_d, total_proof, debtors_contracts
):
    """
    Upload the ZK proof for the entity's receivables to the ZK_Receivables contract.
    Args:
        entity_contract (dict): A dictionary containing the information about the deployed ZK_Receivables contract for the entity.
        proofs (dict): A dictionary containing the generated ZK proofs for each receivable.
        binary_proof_d (dict): A dictionary containing the generated binary proofs for d[i] for each receivable.
        total_proof (dict): A dictionary containing the generated ZK proof for the total balance commitment for the entity's receivables.
        debtors_contracts (dict): A dictionary containing the information about the debtors' contracts.
    """

    # Upload the ZK proofs for the entity's receivables to the ZK_Receivables contract
    print(
        "Uploading ZK proof for the entity's receivables to the ZK_Receivables contract...\n"
    )
    # Code to upload the ZK proof for the entity's receivables to the ZK_Receivables contract using a function in the contract that accepts the proof and any necessary information for verification

    for receivables_id, proof in proofs.items():
        debtors_contract = debtors_contracts[receivables_id][
            "Contract"
        ].address  # Get the contract address for the receivable from the debtors_contracts dictionary

        # Compress the commitments for the receivable using the Pedersen scheme to prepare them for uploading to the ZK_Receivables contract

        for commitment in ["c1", "c2", "c3", "T1", "T2", "T3", "T4", "hvik"]:
            proof[commitment] = zk_snark.compress_point(proof[commitment])

        # Upload the commitment for the receivable to the ZK_Receivables contract using the set_receivable function

        transaction = entity_contract["Contract"].set_ZK_receivable(
            (
                receivables_id,  # The ID number of the debtor's receivable for which the proof is being uploaded
                debtors_contract,  # Address of the debtor's ZK_Debtors contract
                (
                    proofs[receivables_id]["c1"][0],  # c1 Payable commitment x value
                    proofs[receivables_id]["c1"][1],
                ),  # c1 Payable commitment even or odd
                (
                    proofs[receivables_id]["c2"][0],  # c2 Commitment x value
                    proofs[receivables_id]["c2"][1],
                ),  # c2 Commitment even or odd
                (
                    proofs[receivables_id]["c3"][0],  # c3 Commitment x value
                    proofs[receivables_id]["c3"][1],
                ),  # c3 Commitment even or odd
                (
                    proofs[receivables_id]["T1"][0],  # T1 Commitment x value
                    proofs[receivables_id]["T1"][1],
                ),  # T1 Commitment even or odd
                (
                    proofs[receivables_id]["T2"][0],  # T2 Commitment x value
                    proofs[receivables_id]["T2"][1],
                ),  # T2 Commitment even or odd
                (
                    proofs[receivables_id]["T3"][0],  # T3 Commitment x value
                    proofs[receivables_id]["T3"][1],
                ),  # T3 Commitment even or odd
                (
                    proofs[receivables_id]["T4"][0],  # T4 Commitment x value
                    proofs[receivables_id]["T4"][1],
                ),  # T4 Commitment even or odd
                (
                    proofs[receivables_id]["hvik"][0],  # h^vik Commitment x value
                    proofs[receivables_id]["hvik"][1],
                ),  # h^vik Commitment even or odd
                proofs[receivables_id]["s1"],  # Proof s1 value
                proofs[receivables_id]["s2"],  # Proof s2 value
                proofs[receivables_id]["s3"],  # Proof s3 value
                proofs[receivables_id]["s4"],  # Proof s4 value
                proofs[receivables_id]["s5"],  # Proof s5 value
                proofs[receivables_id]["s6"],  # Proof s6 value
                proofs[receivables_id]["k"],  # Challenge k value for the proof
            ),
            {"from": entity_contract["Account"]},
        )
        transaction.wait(1)
        if de_bug:
            print(
                f"ZK proof for receivable {receivables_id} uploaded to ZK_Receivables contract for the entity.\n"
            )  # Print the details of the ZK proof upload for the receivable

        # Compress the commitments for d[i] for the receivable using the ZK Binary SNARK to prepare them for uploading to the ZK_Receivables contract
        for commitment in ["l", "a0", "a1"]:
            binary_proof_d[receivables_id][commitment] = zk_snark.compress_point(
                binary_proof_d[receivables_id][commitment]
            )

        # Upload the binary ZK proof for d[i] for the receivable to the ZK_Receivables contract using the set_ZK_receivable_binary function
        transaction = entity_contract["Contract"].set_ZK_receivable_binary(
            (
                receivables_id,  # The ID number of the debtor's receivable for which the proof is being uploaded
                debtors_contract,  # Address of the debtor's ZK_Debtors contract
                (
                    binary_proof_d[receivables_id]["l"][0],  # l Commitment x value
                    binary_proof_d[receivables_id]["l"][1],
                ),  # l Commitment even or odd
                (
                    binary_proof_d[receivables_id]["a0"][0],  # a0 Commitment x value
                    binary_proof_d[receivables_id]["a0"][1],
                ),  # a0 Commitment even or odd
                (
                    binary_proof_d[receivables_id]["a1"][0],  # a1 Commitment x value
                    binary_proof_d[receivables_id]["a1"][1],
                ),  # a1 Commitment even or odd
                binary_proof_d[receivables_id]["k"],  # challenge k value
                binary_proof_d[receivables_id]["pi"][0],  # Proof c1 value
                binary_proof_d[receivables_id]["pi"][1],  # Proof r0 value
                binary_proof_d[receivables_id]["pi"][2],  # Proof r1 value
            ),
            {"from": entity_contract["Account"]},
        )
        transaction.wait(1)
        if de_bug:
            print(
                f"Binary ZK proof for d for receivable {receivables_id} uploaded to ZK_Receivables contract for the entity.\n"
            )  # Print the details of the binary ZK proof upload for d for the receivable

    # Total proof uploaded after the loop to upload the proofs for the individual receivables so that the total proof can be generated using the sum of the commitments and randomness for all the receivables in the anonymity sample
    # Compress the commitments for total receivable using the ZK Binary SNARK to prepare them for uploading to the ZK_Receivables contract
    print(f"total_proof: {total_proof}")
    total_proof["sum_c1"] = zk_snark.compress_point(total_proof["sum_c1"])

    # Upload the proof for total receivables to the ZK_Receivables contract using the set_totsl_commitments function
    transaction = entity_contract["Contract"].set_total_commitments(
        (
            total_proof["sum_c1"][0],  # sum_c1 Commitment x value
            total_proof["sum_c1"][1],  # sum_c1 Commitment even or odd
        ),  # contract is expecting a tuple for the total commitment
        total_proof["sum_r_v"],  # sum_r_v value for the total balance
        total_proof["sum_bal"],  # sum_bal value for the total balance commitment
        {"from": entity_contract["Account"]},
    )

    transaction.wait(1)
    if verbose:
        print(
            f"Total proofs for entity uploaded to ZK_Receivables contract for the entity.\n"
        )

    return


def verify_receivables(entity_contract):
    """
    Verify the ZK proof for the entity's receivables using the information stored in the ZK_Receivables contract
    and the ZK_Debtors contract.

    Note: this function is called by the verifier to verify the ZK proof for the entity's receivables 
            using the information stored in the ZK_Receivables contract and the ZK_Debtors contract. 
            The verifier can use this function to verify the ZK proof for the entity's receivables without 
            having to know the details of the commitments and randomness for the individual receivables.
            The only other input is the total receivable balance disclosed by the entity to the verifier.
            
    Args:
        entity_contract (dict): A dictionary containing the information about the deployed ZK_Receivables contract for the entity.
    Returns:
        bool: True if all the ZK proofs for the entity's receivables are verified successfully, False otherwise.
    """

    # Verify the ZK proof for the entity's receivables using the information stored in the ZK_Receivables contract
    print("Testing ZK proof verification on the ZK_Receivables contract...\n")

    all_proofs_verified = False  # Initialize a variable to track if all receivables proofs are verified successfully

    # Verify the total proof for the entity's receivables first before verifying the proofs for the individual receivables to ensure that the total proof is valid before verifying the individual proofs for the receivables
    # Get the total proof information from the ZK_Receivables contract using the get_total_commitments function of the contract
    total_proof_info = entity_contract["Contract"].get_total_commitments(
        {"from": accounts[0]}
    )  # Retrieve the total proof information from the ZK_Receivables contract
    if de_bug:
        print(
            f"Retrieved total proof information for entity's receivables from ZK_Receivables contract: {total_proof_info}\n"
        )  # Print the retrieved total proof information from the ZK_Receivables contract

    # Reassemble the total proof information for the entity's receivables from the retrieved total proof information to prepare it for verification of the total proof for the entity's receivables
    total_proof_com = zk_snark.uncompress_point(
        total_proof_info[0]
    )  # Decompress the total commitment for the entity's receivables using the Pedersen scheme
    total_proof_sum_r_v = total_proof_info[
        1
    ]  # Get the sum_r_v value for the total proof from the retrieved total proof information
    total_proof_sum_bal = total_proof_info[
        2
    ]  # Get the sum_bal value for the total proof from the retrieved total proof information

    # Verify the Pedersen scheme with the retrieved total commitment, sum_r_v and sum_bal for the total proof
    total_rec_verified = ped_scheme.verify(
        total_proof_com, total_proof_sum_bal, total_proof_sum_r_v
    )  # Verify the total proof for the entity's receivables using the Pedersen scheme with the retrieved total commitment, sum_r_v and sum_bal for the total proof

    # Print the result of the verification of the total proof for the entity's receivables and set all_proofs verified to False if the total proof for the entity's receivables failed verification since if the total proof is not verified successfully then there is no need to verify the proofs for the individual receivables as the total proof is an aggregate proof that relies on the validity of the proofs for the individual receivables
    if total_rec_verified:
        all_proofs_verified = True
        print(
            f"Total proof for entity's receivables balance is verified successfully.\n"
        )  # Print a message if the total proof for the entity's receivables is verified successfully
    else:
        all_proofs_verified = False
        print(
            f"Total proof for entity's receivables failed verification.\n"
        )  # Print a message if the total proof for the entity's receivables failed verification
        return False  # Return False if the total proof for the entity's receivables failed verification

    # Retrieve the necessary information for verifying the ZK proofs for the receivables from the ZK_Receivables contract to prepare for verifying the proofs for the individual receivables for the entity
    # Information about the individual receivables for the entity is stored in the ZK_Receivables contract 
    # and can be retrieved using the get_ZK_receivables function of the contract

    retrieved_receivables = entity_contract[
        "Contract"
    ].get_ZK_receivables()  # Retrieve the receivable information from the ZK_Receivables contract

    proof = (
        {}
    )  # Create a dictionary to store the uncompressed commitments for the proof verification for the receivable

    for receivable in retrieved_receivables:

        if de_bug:
            print(
                f"Retrieved receivable information for receivable {receivable[0]} from ZK_Receivables contract: {receivable}\n"
            )  # Print the retrieved receivable information from the ZK_Receivables contract

        # Reassemble the proof information for the receivable from the retrieved receivable information to prepare it for verification of the ZK proof for the receivable
        receivable_id = receivable[
            0
        ]  # Get the receivable ID from the retrieved receivable information
        debtors_contract = receivable[
            1
        ]  # Get the debtor's contract address from the retrieved receivable information
        
        
        # Unpack the proof information for the receivable from the retrieved receivable information 
        # to prepare it for verification of the ZK proof for the receivable
        proof[receivable_id] = {
            "c1": zk_snark.uncompress_point(
                receivable[2][0:2]
            ),  # Get the commitment c1 for the receivable from the retrieved receivable information
            "c2": zk_snark.uncompress_point(
                receivable[3][0:2]
            ),  # Get the commitment c2 for the receivable from the retrieved receivable information
            "c3": zk_snark.uncompress_point(
                receivable[4][0:2]
            ),  # Get the commitment c3 for the receivable from the retrieved receivable information
            "T1": zk_snark.uncompress_point(
                receivable[5][0:2]
            ),  # Get the commitment T1 for the receivable from the retrieved receivable information
            "T2": zk_snark.uncompress_point(
                receivable[6][0:2]
            ),  # Get the commitment T2 for the receivable from the retrieved receivable information
            "T3": zk_snark.uncompress_point(
                receivable[7][0:2]
            ),  # Get the commitment T3 for the receivable from the retrieved receivable information
            "T4": zk_snark.uncompress_point(
                receivable[8][0:2]
            ),  # Get the commitment T4 for the receivable from the retrieved receivable information
            "hvik": zk_snark.uncompress_point(
                receivable[9][0:2]
            ),  # Get the h^vik value for the proof from the retrieved receivable information
            "s1": receivable[
                10
            ],  # Get the proof value s1 for the receivable from the retrieved receivable information
            "s2": receivable[
                11
            ],  # Get the proof value s2 for the receivable from the retrieved receivable information
            "s3": receivable[
                12
            ],  # Get the proof value s3 for the receivable from the retrieved receivable information
            "s4": receivable[
                13
            ],  # Get the proof value s4 for the receivable from the retrieved receivable information
            "s5": receivable[
                14
            ],  # Get the proof value s5 for the receivable from the retrieved receivable information
            "s6": receivable[
                15
            ],  # Get the proof value s6 for the receivable from the retrieved receivable information
            "k": receivable[
                16
            ],  # Get the challenge value k for the proof from the retrieved receivable information
        }

        # Get the debtors commitment from their contract to use in the verification of the ZK proof for the receivable
        debtor_contract_instance = ZK_Debtors.at(debtors_contract)
        debtor_commitment = debtor_contract_instance.get_commitments(
            {"from": accounts[0]}
        )  # Retrieve the commitment for the debtor from their ZK_Debtors contract
        delta = zk_snark.uncompress_point(
            debtor_commitment[0][1:3]
        )  # Decompress the retrieved commitment for the debtor using the Pedersen scheme

        if de_bug:
            print(
                f"Debtor {receivable_id} commitment retrieved for ZK proof verification: {delta}"
            )

        # Use the verify_ZK_proof function to verify the ZK proof for the receivable using the retrieved proof information for the receivable and the retrieved commitment for the debtor
        verified = verify_ZK_proof(
            proof[receivable_id], delta
        )  # Verify the ZK proof for the receivable using the verify_ZK_proof function

        # update the all_proofs_verified variable to False if any of the proofs for the individual receivables failed verification since all proofs for the individual receivables need to be verified successfully for the overall verification of the entity's receivables to be successful
        if not verified:
            all_proofs_verified = False  # Set all_proofs_verified to False if any of the proofs for the individual receivables failed verification
            return False  # Return False if any of the proofs for the individual receivables failed verification

        print(
            f"ZK proof verification for receivable {receivable_id}: {verified}\n"
        )  # Print the result of the ZK proof verification for the receivable

    # Verify the binary ZK proof for d[i] for the receivable using the ZK Binary SNARK

    # Retrieve the necessary information for verifying the binary ZK proofs for d[i] for the receivables from the ZK_Receivables contract to prepare for verifying the binary proofs for d[i] for the individual receivables for the entity
    retrieved_binary_proof_d = entity_contract[
        "Contract"
    ].get_ZK_binary_receivables()  # Retrieve the binary proof information for d[i] for the receivables from the ZK_Receivables contract

    binary_proof_d = (
        {}
    )  # Create a dictionary to store the uncompressed commitments for the binary proof for d[i] for the proof verification for the receivable

    for receivable in retrieved_binary_proof_d:

        # Reassemble the proof information for the receivable from the retrieved receivable information to prepare it for verification of the ZK proof for the receivable
        receivable_id = receivable[
            0
        ]  # Get the receivable ID from the retrieved receivable information
        debtors_contract = receivable[
            1
        ]  # Get the debtor's contract address from the retrieved receivable information

        if de_bug:
            print(
                f"Retrieved binary proof information for d for receivable {receivable_id} from ZK_Receivables contract: {receivable}\n"
            )  # Print the retrieved binary proof information for d[i] for the receivable from the ZK_Receivables contract

        # Reassemble the binary proof information for d[i] for the receivable from the retrieved binary proof information to prepare it for verification of the binary ZK proof for d[i] for the receivable
        binary_proof_d[receivable_id] = {
            "l": zk_snark.uncompress_point(
                receivable[2][0:2]
            ),  # Get the commitment l for the binary proof for d[i] for the receivable from the retrieved binary proof information
            "a0": zk_snark.uncompress_point(
                receivable[3][0:2]
            ),  # Get the commitment a0 for the binary proof for d[i] for the receivable from the retrieved binary proof information
            "a1": zk_snark.uncompress_point(
                receivable[4][0:2]
            ),  # Get the commitment a1 for the binary proof for d[i] for the receivable from the retrieved binary proof information
            "k": receivable[
                5
            ],  # Get the challenge value k for the binary proof for d[i] for the receivable from the retrieved binary proof information
            "pi": (
                receivable[
                    6
                ],  # Get the proof value c1 for the binary proof for d[i] for the receivable from the retrieved binary proof information
                receivable[
                    7
                ],  # Get the proof value r0 for the binary proof for d[i] for the receivable from the retrieved binary proof information
                receivable[
                    8
                ],  # Get the proof value r1 for the binary proof for d[i] for the receivable from the retrieved binary proof information
            ),
        }
        binary_proof_valid = zk_snark.verify(
            binary_proof_d[receivable_id]
        )  # Verify the binary ZK proof for d[i] for the receivable using the ZK Binary SNARK

        print(
            f"Binary ZK proof verification for d for receivable {receivable_id}: {binary_proof_valid}\n"
        )  # Print the result of the binary ZK proof verification for d[i] for the receivable

        if not binary_proof_valid:
            all_proofs_verified = False  # Set all_proofs_verified to False if the binary proof for d[i] for the receivable failed verification
            return False  # Return False if the binary proof for d[i] for the receivable failed verification

    return all_proofs_verified  # Return True if all proofs for the entity's receivables are verified successfully, False otherwise


def main():

    no_of_debtors = 20  # Example number of debtors
    no_of_receivables = 5  # Example number of receivables
    no_of_anonymity_sample = 10  # Example number of anonymity samples

    debtors, sample_receivables = generate_sample_data(
        no_of_debtors, no_of_receivables, no_of_anonymity_sample
    )  # Generate the sample data for the debtors and receivables

    # Debtors: Deploy the ZK_Debtors contracts with the debtors commitments
    debtors_contracts = deploy_ZK_Debtors(
        debtors
    )  # Deploy the ZK_Debtors contract for each debtor
    # return value has information about the deployed contracts for each debtor

    debtors_contracts = upload_commitments(
        debtors_contracts
    )  # Calculate and upload the commitments for each debtor to the ZK_Debtors contract
    # return value has information about the commitments for each debtor

    sample_receivables = communicate_r_to_entity(debtors_contracts, sample_receivables)
    # Communicate the randomness r for the commitments from the debtors to the entity for generating ZK proofs
    # return value has the updated sample_receivables dictionary with the communicated randomness r for generating ZK proofs

    entity_contract = deploy_ZK_Receivables()
    # Deploy the ZK_Receivables contract for the entity

    # Entity:Generate the ZK proof for the entity's receivables
    proofs, binary_proof_d, total_proof = generate_ZK_proof(
        sample_receivables, debtors_contracts
    )  # Generate the ZK proofs and binary proof for the entity's receivables

    # Upload the ZK proof for the entity's receivables to the ZK_Receivables contract
    upload_ZK_proofs(
        entity_contract, proofs, binary_proof_d, total_proof, debtors_contracts
    )

    # # Auditor/Public: Verification on the ZK_Receivables contract
    all_verified = verify_receivables(
        entity_contract
    )  # ZK proof verification on the ZK_Receivables contract

    if all_verified:
        print(
            f"All ZK proofs for the entity's receivables are verified successfully on the ZK_Receivables contract.\n"
        )  # Print a message if all ZK proofs for the entity's receivables are verified successfully on the ZK_Receivables contract
    else:
        print(
            f"ZK proof verification for the entity's receivables failed on the ZK_Receivables contract.\n"
        )  # Print a message if ZK proof verification for the entity's receivables failed on the ZK_Receivables contract
