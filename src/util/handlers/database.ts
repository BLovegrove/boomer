import config from "../../config.json"

import mongoDB, {MongoClient} from "mongodb";

export const collections: { favs?: mongoDB.Collection, idleTracks?: mongoDB.Collection } = {}

export async function connect() {

	const client: MongoClient = new MongoClient(config.db.mongoURI);

	await client.connect();

	const db: mongoDB.Db = client.db(config.db.name);

	const favsCollection: mongoDB.Collection = db.collection(config.db.collections.favs);
	const idleTracksCollection: mongoDB.Collection = db.collection(config.db.collections.idleTracks);

	collections.favs = favsCollection;
	collections.idleTracks = idleTracksCollection;

	console.log(`Successfully connected to database: ${db.databaseName}`);
	console.log('Acquired collections:');
	console.log(collections)
}