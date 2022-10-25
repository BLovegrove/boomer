import express, { Request, Response } from "express";
import { ObjectId } from "mongodb";
import { collections } from "../handlers/database";
import Favs from "../models/favs";

// Global Config

export const favsRouter = express.Router();

favsRouter.use(express.json());

// GET

favsRouter.get("/", async (_request: Request, response: Response) => {
	try {
		const favs = (await collections.favs?.find({}).toArray()) as Favs[];

		response.status(200).send(favs);
		
	} catch (error) {
		response.status(500).send(error);
	}
});

favsRouter.get("/role/:roleID", async (request: Request, result: Response) => {
	const role = request?.params?.role;

	try {
		const query = {_roleID: role};
		const favs = (await collections.favs?.findOne(query)) as Favs;

		if (favs) {
			result.status(200).send(favs);
		}
	} catch (error) {
		console.log(request.params)
		result.status(404).send(`Unable to find matching document with role id: ${request.params.role}`)
	}
})

// finds single item by Document ID
favsRouter.get("/id/:id", async (request: Request, result: Response) => {
	const id = request?.params?.id;

	try {

		const query = { _id: new ObjectId(id) };
		const favs = (await collections.favs?.findOne(query)) as Favs;

		if (favs) {
			result.status(200).send(favs);
		}
	} catch (error) {
		result.status(404).send(`Unable to find matching document with id: ${request.params.id}`);
	}
});

// POST

favsRouter.post("/", async (request: Request, result: Response) => {
	try {
		const newFav = request.body as Favs;
		const insertResult = await collections.favs?.insertOne(newFav);

		insertResult
			? result.status(201).send(`Successfully created a new favs list with id ${insertResult.insertedId}`)
			: result.status(500).send("Failed to create a new favs list.");
	} catch (error) {
		console.error(error);
		result.status(400).send(error);
	}
});

// PUT

favsRouter.put("/id/:id", async (request: Request, result: Response) => {
	const id = request?.params?.id;

	try {
		const updatedFavs: Favs = request.body as Favs;
		const query = { _id: new ObjectId(id) };

		const updateResult = await collections.favs?.updateOne(query, { $set: updatedFavs });

		updateResult
			? result.status(200).send(`Successfully updated favs list with id ${id}`)
			: result.status(304).send(`Favs list with id: ${id} not updated`);
	} catch (error) {
		console.error(error);
		result.status(400).send(error);
	}
});

// DELETE

favsRouter.delete("/:id", async (request: Request, result: Response) => {
	const id = request?.params?.id;

	try {
		const query = { _id: new ObjectId(id) };
		const deleteResult = await collections.favs?.deleteOne(query);

		if (deleteResult && deleteResult.deletedCount) {
			result.status(202).send(`Successfully removed favs list with id ${id}`);
		} else if (!deleteResult) {
			result.status(400).send(`Failed to remove favs list with id ${id}`);
		} else if (!deleteResult.deletedCount) {
			result.status(404).send(`Favs list with id ${id} does not exist`);
		}
	} catch (error) {
		console.error(error);
		result.status(400).send(error);
	}
});