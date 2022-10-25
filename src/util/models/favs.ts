import { ObjectId } from "mongodb";

export default class Favs {
	constructor(public _roleID: string, public _tracks: Array<Object>, public _id?: ObjectId) {

	}
}