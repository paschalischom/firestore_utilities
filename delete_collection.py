import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

total_deletes = 0
COLLECTION_NAME = ''


# A fully recursive function that deletes a collection given its top level reference.
# It's able to detect and delete all subcollections. The secret lies in creating a
# an array of document references from the document snapshots retrieved for a given collection.
# When modifying the structure of a collection while iterating, we want to hold onto the references
# and not the actual snapshots.
# Check https://github.com/googleapis/google-cloud-python/issues/6033.
def delete_collection(coll_ref, batch_size):
    global total_deletes
    print(f'Entering collection: "{coll_ref.id}"')
    docs = coll_ref.limit(batch_size).stream()
    doc_refs = [doc.reference for doc in docs]
    deleted = 0

    for doc_ref in doc_refs:
        subcolls_ref = coll_ref.document(doc_ref.id).collections()
        print(f'--Checking doc "{doc_ref.id}" for subcollections')
        for subcoll_ref in subcolls_ref:
            delete_collection(subcoll_ref, batch_size)
        print(f'----Deleting doc "{doc_ref.id}"')
        doc_ref.delete()
        deleted += 1
        total_deletes += 1
        if total_deletes >= 20000:
            print(f'Returning due to quota limit.')
            return

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def main():
    cred = credentials.Certificate('<YOUR_SERVICE_ACCOUNT_KEY>.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    # EDIT THE LINE BELOW WITH THE REFERENCE TO YOUR COLLECTION OR SUBCOLLECTION
    # e.g. top-level collection: db.collection('<collection_name>')
    #      second-level subcollection: db.collection('<collection_name>').document('<doc_name>').collection('<collection_name>')
    rootNode = db.collection(COLLECTION_NAME)
    delete_collection(rootNode, 500)
    print(f'Documents deleted: {total_deletes}')


if __name__ == "__main__":
    main()
