# ZKSnark Implementation
# Author: **** *******
# Date: 2024-06-10
# License: MIT License

from abc import ABC, abstractmethod
import tinyec.ec as tiny
import tinyec.registry as reg
import secrets
import random
import hashlib
from sys import getsizeof
from nummaster.basic import sqrtmod
from pedersen_scheme import Ped_scheme


class ZKBase(ABC):
    def __init__(self):
        # Initialize Pedersen Commitment Scheme which is used by ZK proofs
        self.ped = Ped_scheme()
        # Copy relevant parameters from Pedersen scheme
        self.n = self.ped.n
        self.p = self.ped.p
        self.a = self.ped.a
        self.b = self.ped.b
        self.G = self.ped.curve.g
        self.H = self.ped.H
        self.curve = self.ped.curve
        self.randn = self.ped.randn  # Copy randn method from Pedersen scheme

    def compress_point(self, point):
        """Compresses a point on an Elliptic Curve. Returns x value and boolean

        Args:
            point (tinyec point): tinyec point e.g. curve.g.x

        Returns:
            tuple: (x value of point, boolean)
        """
        # Input validation
        # Check if input is a tiny.Point
        if not isinstance(point, tiny.Point):
            raise ValueError("Input must be a tiny.Point instance")
        return (point.x, point.y % 2)

    def uncompress_point(self, compressed_point):
        """Uncompress a point on an Elliptic Curve.

        Args:
            point (compressed point): x value of point and boolean

        Returns:
            tinyec point: point on elliptic curve
        """
        # Check if input is a tuple
        if not isinstance(compressed_point, tuple) or len(compressed_point) != 2:
            raise ValueError("Input must be a tuple of (x, is_odd)")

        x, is_odd = compressed_point
        y = sqrtmod(pow(x, 3, self.p) + self.a * x + self.b, self.p)
        if bool(is_odd) == bool(y & 1):
            return tiny.Point(self.curve, x, y)
        return tiny.Point(self.curve, x, self.p - y)

    def generate_challenge(self, *commitments):
        """Generates a challenge integer based on the given commitments.

        Args:
            points on the elliptic curve: tiny points

        Returns:
            int: challenge integer

        """
        sha = hashlib.sha256()
        for point in commitments:
            if hasattr(point, "x"):
                x_val, is_odd = self.compress_point(point)
                sha.update(f"{x_val}{is_odd}".encode())
            else:
                sha.update(str(point).encode())
        return int(sha.hexdigest(), 16) % self.n

    def short(self, x):
        """Utility for pretty-printing large integers or point coordinates."""
        s = str(x)
        return s[:10] + "..." if len(s) > 10 else s

    @abstractmethod
    def prove(self, secret, **kwargs):
        """Standard interface for generating a proof."""
        pass

    @abstractmethod
    def verify(self, proof, **kwargs):
        """Standard interface for verifying a proof."""
        pass


# Test the ZKBase class functionality

debug = False


# Create an instance of the Pedersen Commitment scheme
class ZK_generic(ZKBase):
    def prove(self, secret, **kwargs):
        pass

    def verify(self, proof, **kwargs):
        pass


p = Ped_scheme()
zk = ZK_generic()

if debug:
    print("Testing ZKBase class functionality...\n")

# Test 1: Compress and uncompress a point
point = p.commit(10, 20)
compressed = zk.compress_point(point)
uncompressed = zk.uncompress_point(compressed)
assert point == uncompressed, "Point compression/uncompression failed!"
if debug:
    print("ZKBase Test - Point Compression/Uncompression:")
    print(f"Original Point: ({zk.short(point.x)}, {zk.short(point.y)})")
    print(f"Compressed Point: {compressed}")
    print(
        f"Uncompressed Point: ({zk.short(uncompressed.x)}, {zk.short(uncompressed.y)})\n"
    )

# Test 2: Generate challenge
point2 = p.commit(30, 40)
point3 = p.commit(50, 60)
challenge = zk.generate_challenge(point, point2, point3)
assert isinstance(challenge, int), "Challenge generation failed!"
if debug:
    print("ZKBase Test - Challenge Generation:")
    print(f"Generated Challenge: {challenge}\n")

# Test 3: Short utility
large_int = 12345678901234567890
shortened = zk.short(large_int)
assert shortened == "1234567890...", "Short utility failed!"
if debug:
    print("ZKBase Test - Short Utility:")
    print(f"Original Integer: {large_int}")
    print(f"Shortened: {shortened}\n")

# Test 4 : Test randn function copied from Pedersen scheme
rand_num = zk.randn()
assert isinstance(rand_num, int), "randn function failed!"
if debug:
    print("ZKBase Test - randn Function:")
    print(f"Random Number: {rand_num}")


####################################################
# A class for the zk-Binary Snark proof system.    #
####################################################


class ZkBinarySnark(ZKBase):
    debug = False  # Set to True to enable debug prints

    def generate_commitments(self, secret):
        """
        Generates commitments for the given binary secret.

        Args:
            secret (int): The binary secret value to commit to.

        Returns:
            dict: The commitments containing keys 'l', 'y', 'a0', 'a1', 'cf', 'u0', and 'u1'.
        """
        # Check that the secret is binary
        if secret not in [0, 1]:
            raise ValueError("Secret must be a binary value (0 or 1).")

        # Generate random values for the proof
        y = self.randn()  # random number for the commitment to the secret
        cf = self.randn()  # random number for the binary commitment to the secret
        u0 = self.randn()  # random number for the random commitment
        u1 = self.randn()  # random number for the random commitment

        # Prover generates commitments
        l = secret * self.G + y * self.H  # commitment to the secret C(secret,y)
        a0 = (
            -secret * cf
        ) * self.G + u0 * self.H  # commitment to -secret * cf C(-secret*cf,u0)
        a1 = (
            (1 - secret) * cf
        ) * self.G + u1 * self.H  # commitment to (1-secret) * cf C((1-secret)*cf,u1)

        if self.debug:
            print("Commitments")
            print("-------------------")
            print(
                f"secret: {secret} y: {self.short(y)} cf: {self.short(cf)} u0: {self.short(u0)} u1: {self.short(u1)}"
            )
            print(f"l: ({self.short(l.x)}, {self.short(l.y)}...)")
            print(f"a0: ({self.short(a0.x)}, {self.short(a0.y)})")
            print(f"a1: ({self.short(a1.x)}, {self.short(a1.y)})")
            print("-------------------")

            # Test the commitments
            if secret == 1:
                assert l == self.G + y * self.H
                assert a0 == (-cf) * self.G + u0 * self.H
                assert a1 == 0 * self.G + u1 * self.H
            else:
                assert l == 0 * self.G + y * self.H
                assert a0 == 0 * self.G + u0 * self.H
                assert a1 == cf * self.G + u1 * self.H

        return {"l": l, "a0": a0, "a1": a1, "y": y, "cf": cf, "u0": u0, "u1": u1}

    def prove(self, commitments, secret, challenge):
        """
        Generates a zk Binary SNARK proof for the given secret.

        Args:
            commitments (dict): The commitments containing keys 'l', 'a0', 'a1', 'y', 'cf', 'u0', and 'u1'.
            secret (int): The secret value to prove knowledge of.
            challenge (int): The verifier's challenge value.

        Returns:
            dict: The zk-SNARK proof containing keys 'l', 'a0', 'a1', 'k', and 'pi'.
            pi is a tuple of (c1, r0, r1).
        """

        k = challenge % self.n  # verifier challenge
        y = commitments["y"]
        cf = commitments["cf"]
        u0 = commitments["u0"]
        u1 = commitments["u1"]
        l = commitments["l"]
        a0 = commitments["a0"]
        a1 = commitments["a1"]

        # Prover calculates the proof
        c1 = (secret * (k - cf) + (1 - secret) * cf) % self.n
        r0 = (u0 + (k - c1) * y) % self.n
        r1 = (u1 + c1 * y) % self.n

        pi = (c1, r0, r1)  # proof (tuple of c1,r0,r1)

        if self.debug:
            print("Proof Generation")
            print("-------------------")
            print(
                f"c1: {self.short(c1)} r0: {self.short(r0)} r1: {self.short(r1)} k: {self.short(k)}"
            )
            print("-------------------")

        return {"l": l, "a0": a0, "a1": a1, "k": k, "pi": pi}

        return hash_output

    def verify(self, proof):
        """
        Verifies the zk-SNARK proof.

        Args:
            proof (dict): The zk-SNARK proof to verify. Must contain keys 'l', 'a0', 'a1', 'k', and 'pi'.

        Returns:
            bool: True if the proof is valid, False otherwise.

        """

        l = proof["l"]  # commitment to the secret C(x,r)
        a0 = proof["a0"]  # commitment to the randomness C(t1,t2))
        a1 = proof["a1"]  # commitment to the randomness C(t1,t2))
        pi = proof["pi"]  # proof (tuple of s1,s2)
        k = proof["k"]  # verifier challenge

        # Verifier checks the proof
        c1, r0, r1 = pi

        lhs0 = r0 * self.H
        rhs0 = a0 + l * (k - c1)

        lhs1 = r1 * self.H
        # rhs1 = a1 + (l + (self.G * -1)) * c1
        rhs1 = a1 + (l - self.G) * c1

        if self.debug:
            print("Proof Verification")
            print("-------------------")
            print(f"l: ({self.short(l.x)}, {self.short(l.y)}...)")
            print(f"a0: ({self.short(a0.x)}, {self.short(a0.y)})")
            print(f"a1: ({self.short(a1.x)}, {self.short(a1.y)})")
            print(
                f"c1: {self.short(c1)} r0: {self.short(r0)} r1: {self.short(r1)} k: {self.short(k)}"
            )
            print(f"k - c1: {self.short(k - c1)}")
            print(f"lhs0: ({self.short(lhs0.x)}, {self.short(lhs0.y)})")
            print(f"rhs0: ({self.short(rhs0.x)}, {self.short(rhs0.y)})")
            print(f"lhs1: ({self.short(lhs1.x)}, {self.short(lhs1.y)})")
            print(f"rhs1: ({self.short(rhs1.x)}, {self.short(rhs1.y)})")
            print("-------------------")

        if lhs0 == rhs0 and lhs1 == rhs1:
            return True
        else:
            return False

    def print_proof(self, proof):
        """
        Prints the zk Binary SNARK proof in a readable format.

        Args:
            proof (dict): The zk Binary SNARK proof to print. Must contain keys 'l', 'a0', 'a1', 'k' and 'pi'.

        """

        l = proof["l"]
        a0 = proof["a0"]
        a1 = proof["a1"]
        k = proof["k"]
        pi = proof["pi"]
        c1, r0, r1 = pi

        print("ZK Binary SNARK Proof:")
        print(
            f"Binary Commitment to Secret (l - (x,y) on EC): ({self.short(l.x)}, {self.short(l.y)}...)"
        )
        print(
            f"Commitment to Randomness (a0 - (x,y) on EC): ({self.short(a0.x)}, {self.short(a0.y)})"
        )
        print(
            f"Commitment to Randomness (a1 - (x,y) on EC): ({self.short(a1.x)}, {self.short(a1.y)})"
        )
        print(f"Challenge (k): {self.short(k)}")
        print(
            f"Proof (c1, r0, r1): ({self.short(c1)}, {self.short(r0)}, {self.short(r1)})"
        )


# Tests for the ZkBinarySnark class 

if debug:
    print("Testing ZkBinarySnark class functionality...\n")

zk_binary_snark_test = ZkBinarySnark()

# Test for zk Binary SNARK proof generation and verification

# Test for 1
secret = 1  # Example binary secret
commitments = zk_binary_snark_test.generate_commitments(secret)
challenge = zk_binary_snark_test.generate_challenge(
    commitments["l"], commitments["a0"], commitments["a1"]
)
proof = zk_binary_snark_test.prove(commitments, secret, challenge)
is_valid = zk_binary_snark_test.verify(proof)
assert is_valid, "ZK Binary SNARK proof verification failed!"
if debug:
    print("ZK Binary SNARK proof for 1 verification successful!\n")

# Test for 0
secret = 0  # Example binary secret
commitments = zk_binary_snark_test.generate_commitments(secret)
challenge = zk_binary_snark_test.generate_challenge(
    commitments["l"], commitments["a0"], commitments["a1"]
)
proof = zk_binary_snark_test.prove(commitments, secret, challenge)
is_valid = zk_binary_snark_test.verify(proof)
assert is_valid, "ZK Binary SNARK proof verification failed!"
if debug:
    print("ZK Binary SNARK proof for 0 verification successful!\n")


# Example usage of the ZkBinarySnark class
if __name__ == "__main__":
    zk_binary_snark = ZkBinarySnark()

    random.seed(42)  # For reproducibility in this example

    # Prover's secret (binary value)
    secret = 1  # Example binary secret
    # Prover generates commitments
    commitments = zk_binary_snark.generate_commitments(secret)
    # Verifier generates challenge
    challenge = zk_binary_snark.generate_challenge(
        commitments["l"], commitments["a0"], commitments["a1"]
    )
    # Prover generates proof
    proof = zk_binary_snark.prove(commitments, secret, challenge)
    # Verifier verifies proof
    is_valid = zk_binary_snark.verify(proof)
    zk_binary_snark.print_proof(proof)
    print(f"Proof valid: {is_valid}")
    assert is_valid, "ZK Binary SNARK proof verification failed!"
