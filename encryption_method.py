import tenseal as ts

def initialize_encryption_context():
    """
    Initializes and returns a TenSEAL CKKS encryption context with optimized parameters.
    """
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192)
    context.generate_galois_keys()
    # Adjust scale for your needs
    context.global_scale = 2**40
    return context

def encrypt_face_embedding(face_embedding, context):
    """
    Encrypts a face embedding vector using the provided TenSEAL context.
    :param face_embedding: A list or array of floats representing the face embedding.
    :param context: A TenSEAL context.
    :return: Serialized encrypted face vector (bytes).
    """
    enc_vector = ts.ckks_vector(context, face_embedding)
    return enc_vector.serialize()
