import { ObjectId } from "mongodb";

export default class IdleTrack {
	constructor(public memberID: string, public track: string, public _id?: ObjectId) {

	}
}