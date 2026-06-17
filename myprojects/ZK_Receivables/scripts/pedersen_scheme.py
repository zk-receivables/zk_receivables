# Pedersen Commitment Scheme Implementation
# Author: **** *******
# Date: 2024-06-10
# License: MIT License

import random
import tinyec.ec as tiny
import tinyec.registry as reg
from nummaster.basic import sqrtmod


##########################################################
# A class for the Pedersen Commitment Scheme.            #
# Using the tinyec library for elliptic curve operations #
##########################################################

class Ped_scheme:
    # Class level variables
    # Parameters of the elliptic curve

    # Domain parameters for the `secp256k1` curve
    # (as defined in http://www.secg.org/sec2-v2.pdf)
    name = "secp256k1"
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    a = 0x0000000000000000000000000000000000000000000000000000000000000000
    b = 0x0000000000000000000000000000000000000000000000000000000000000007
    g = (
        0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    )
    h = 1
    curve = tiny.Curve(a, b, tiny.SubGroup(p, g, n, h), name)

    # Value of H_x is SHA256 of G.x in Bitcoin
    # https://github.com/AdamISZ/ConfidentialTransactionsDoc/blob/master/essayonCT.pdf
    # Page 6

    H_x = 36444060476547731421425013472121489344383018981262552973668657287772036414144
    H_y = 22537504475708154238330251540244790414456712057027634449505794721772594235652
    H = tiny.Point(curve, H_x, H_y)

    def is_a_curve_point(self, point):
        """Check if a point is on the elliptic curve.

        Args:
            point (tinyec point): point on elliptic curve
        Returns:
            bool: True if point is on the curve, False otherwise
        """
        # Input validation
        if not isinstance(point, tiny.Point):
            raise ValueError("Input must be a tiny.Point instance")
        return point.on_curve

    # Utility functions to generate random numbers
    def randn(self):
        """
        Generates a random number between 1 and the order of the elliptic curve -1 .

        Returns:
            int: random number less than the order of the elliptic curve (n - 1).
        """
        return random.randint(1, self.n - 1)

    def commit(self, v, r=None):
        """Generate Pedersen Commitment

        Args:
            v (integer): value to be committed to
            r (integer, optional): random number used for the commitment. If None, a random number is generated.

        Returns:
            tinyec point: point on elliptic curve
            r (integer): random number below order (p) of elliptic curve. Only returned where r is None
        """

        # Input validation
        if not isinstance(v, int) or v < 0:
            raise ValueError("Value v must be a non-negative integer")
        if r is not None and not isinstance(r, int):
            raise ValueError("Random number r must be an integer")

        # Modular reduction of the value
        v_reduced = v % self.n

        # use secrets library for better randomness
        if r is None:
            r = self.randn()
            return v * self.curve.g + r * self.H, r
        else:
            # Reduce r modulo n to ensure it is within the valid range
            r = r % self.n
            return v * self.curve.g + r * self.H

    def verify(self, c, v, r):
        """Verify Pedersen Commitment

        Args:
            c (tinyec point on elliptic curve): pedersen commitment
            v (integer): value that was committed
            r (integer): random number used for the commitment

        Returns:
            True/False : Commitment is verified
        """

        # Input validation
        if not isinstance(c, tiny.Point):
            raise ValueError("Commitment c must be a tiny.Point instance")
        if not isinstance(v, int) or v < 0:
            raise ValueError("Value v must be a non-negative integer")
        if not isinstance(r, int):
            raise ValueError("Random number r must be an integer")

        # Reduce v and r modulo n to ensure they are within the valid range
        v_mod = v % self.n
        r_mod = r % self.n

        return c == v_mod * self.curve.g + r_mod * self.H

    def sum_commitments(self, commitments):
        """
        Sums a list of Pedersen commitments.

        Args:
            commitments (list): List of Pedersen commitments (tinyec points).

        Returns:
            tinyec point: The sum of the commitments.
        """
        total_commitment = commitments[0]
        for c in commitments[1:]:
            # Input validation
            if not isinstance(c, tiny.Point):
                raise ValueError("All commitments must be tiny.Point instances")
            # Sum the commitments
            total_commitment += c
        return total_commitment

    def short(self, number):
        """
        Shortens a large integer by returning its first 6 digits followed by ellipsis.

        Args:
            number (int): The large integer to shorten.

        Returns:
            str: The shortened representation of the integer.
        """
        if len(str(number)) <= 6:
            return str(number)
        else:
            return str(number)[:6] + "..."

    def print_commitment(self, commitment):
        """
        Prints the Pedersen commitment in a readable format.

        Args:
            commitment (tinyec point): The Pedersen commitment to print.
        """
        # Input validation
        if not isinstance(commitment, tiny.Point):
            raise ValueError("Commitment must be a tiny.Point instance")
        print(
            f"Pedersen Commitment (C - (x,y) on EC): ({self.short(commitment.x)}, {self.short(commitment.y)}...)"
        )


# Test the Pedersen Commitment scheme
# Create an instance of the Pedersen Commitment scheme
p = Ped_scheme()

# Debug mode
debug = False

# Test 1: Basic commitment with no r and verification

v = 1234567890
c, r = p.commit(v)  # r is returned only when not provided
assert p.verify(c, v, r), "Pedersen Commitment verification failed!"

# Test 2: Commitment with provided r and verification
c1 = p.commit(v, r=r)  # r is not returned when provided
assert c == c1, "Pedersen Commitment with provided r failed!"
assert p.verify(c1, v, r), "Pedersen Commitment verification failed!"

# Test 3: Commitment with new random r and verification
v2 = 1234567890
r2 = p.randn()
c2 = p.commit(v2, r2)  # r is returned only when not provided
assert p.verify(c2, v2, r2), "Pedersen Commitment verification failed!"


# Test 4: Commitment sum and verification
q = 9876543210
c3, r3 = p.commit(q)
c2_plus_c3 = c2 + c3
assert p.verify(
    c2_plus_c3, v2 + q, r2 + r3
), "Pedersen Commitment sum verification failed!"

c_list = [c2, c3]
c3 = p.sum_commitments(c_list)
assert p.verify(
    c3, v2 + q, r2 + r3
), "Pedersen Commitment sum function verification failed!"


# Test 5: Print commitment

if debug:
    print("Ped_scheme Test - Pedersen Commitment:")
    p.print_commitment(c3)

# Test 6: Check if point is on curve
if debug:
    print("Testing if point is on the elliptic curve...")
    print(f"c3 is on curve: {p.is_a_curve_point(c3)}")
assert p.is_a_curve_point(c3), "Point is not on the elliptic curve!"

if debug:
    print("All Pedersen Commitment tests passed successfully!")
