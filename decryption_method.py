import tenseal as ts
import numpy as np

def load_encryption_context(serialized_secret_context):
    """
    Loads and returns a TenSEAL context from the serialized secret context.
    """
    context = ts.context_from(serialized_secret_context)
    return context

def decrypt_face_vector(encrypted_vector, context):
    """
    Decrypts the encrypted face vector using the provided TenSEAL context.
    :param encrypted_vector: The serialized encrypted face vector.
    :param context: A TenSEAL context.
    :return: The decrypted face vector as a list of floats.
    """
    enc_vector = ts.lazy_ckks_vector_from(encrypted_vector)
    enc_vector.link_context(context)
    return enc_vector.decrypt()

def lazy_vector_from_bytes(serialized_encrypted_vector, context):
    """
    Returns a lazy CKKS vector object from serialized bytes, linking the context.
    This is helpful if we want to do partial operations before decrypting.
    """
    enc_vector = ts.lazy_ckks_vector_from(serialized_encrypted_vector)
    enc_vector.link_context(context)
    return enc_vector

def compare_face_vectors(vector1, vector2, threshold=0.6):
    """
    Compares two face vectors by computing the Euclidean distance.
    Typical threshold for face_recognition is around 0.6.
    :param vector1: First face vector (list or array).
    :param vector2: Second face vector (list or array).
    :param threshold: Distance threshold to consider a match.
    :return: (match, distance)
    """
    distance = np.linalg.norm(np.array(vector1) - np.array(vector2))
    match = (distance < threshold)
    return match, distance
