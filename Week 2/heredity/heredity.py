import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Initialize Joint Probability
    joint_probability = 1.0


    for person in people:
        # Count gene for  person
        if person in one_gene:
            gene_count = 1
        elif person in two_genes:
            gene_count = 2
        else:
            gene_count = 0
        
        # Know parents of person
        mother = people[person]["mother"]
        father = people[person]["father"]


        if mother is None and father is None:
            # Base condition: no parents, base gene probability on gene count of person
            gene_probability = PROBS["gene"][gene_count]
        else: 
            # Handle condition: parents known

            def get_parents_probability(parent):
                if parent in one_gene:
                    return 0.5 # Half chance gene from mother or father
                elif parent in two_genes:
                    return 1 - PROBS["mutation"] # High gene probability
                else:
                    return PROBS["mutation"] # Mutation probability if no parents have 'the gene'

            # Get parents probability of transferring genes  
            mother_probability = get_parents_probability(mother)
            father_probability = get_parents_probability(father)
            
            # Based on gene count of person calculate probability of receving parents genes.
            if gene_count == 2: # From both mother and father genes
                gene_probability = mother_probability * father_probability
            elif gene_count == 1: # Either from mother or father genes
                gene_probability = (
                    mother_probability * (1 - father_probability)
                    +
                    father_probability * (1 - mother_probability)
                )
            else: # No gene received from father and mother
                gene_probability = (1- mother_probability) * (1 - father_probability)

        # Calculate Trait probability
        has_trait = person in have_trait
        trait_probability = PROBS["trait"][gene_count][has_trait]
        
        # Calculate Joint Probability_
        joint_probability *= gene_probability * trait_probability

    return joint_probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:

        # Determine gene count
        if person in two_genes:
            gene_count = 2
        elif person in one_gene:
            gene_count = 1
        else:
            gene_count = 0


        # update gene probability based on count
        probabilities[person]["gene"][gene_count] += p

        # Determine current person has trait
        has_trait = person in have_trait

        # person has trait update the probability
        probabilities[person]["trait"][has_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
