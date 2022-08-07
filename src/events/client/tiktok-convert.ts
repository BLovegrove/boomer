// Convert / Download / Upload tiktok links automatically

import { ExtendedClient, ClientEvent } from "../../util/structures";
import { MessageAttachment } from "discord.js";
import { TTScraper } from "tiktok-scraper-ts";
import { TikTokEmbedBuilder } from "../../util/structures/embed-builders";

export const event: ClientEvent = {
    name: "tiktokConvert",
    async listen(client: ExtendedClient) {
        client.on("messageCreate", async (message) => {
            
			// Make sure theres a tiktok link in the mesage and it wasnt sent by a bot or anything
			if (!message.content.includes("vt.tiktok") || message.author.bot || !message.channel) {
				return
			}

			// grab the url using https:// and a consistent query param as the start/finish of the url
			const urlStart = message.content.indexOf("https://")
			// ew magic number. +4 is for the length of the substring its indexing for
			const urlEnd = message.content.indexOf("?k=1") + 4
			const tikTokUrl = message.content.substring(urlStart, urlEnd)

			// save a clean version of the message
			const cleanContent = message.content.replace(tikTokUrl, '{URL}')

			// delete the original messsage
			await message.delete()

			const tikTokPlaceholder = await message.channel.send("Loading TikTok data... (Might take a few seconds)")

			// download the image
			const scraper = new TTScraper()
			const tikTok = await scraper.video(tikTokUrl)
			const tikTokDirect = await scraper.noWaterMark(tikTokUrl)

			if (tikTokDirect) {

				// send the new one
				const tikTokEmbed = new TikTokEmbedBuilder(message, tikTok, cleanContent).toJSON()
				await tikTokPlaceholder.edit({
					content: "TikTok found! :tada:",
					embeds: [tikTokEmbed]
				})
				await message.channel.send(tikTokDirect)

			} else {
				await tikTokPlaceholder.edit("Something went wrong fetching a direct link to your TikTok. Please contact your server admin / bot dev.")
			}

			return
        })
    }
}