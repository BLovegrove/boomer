// Convert / Download / Upload tiktok links automatically

import { ExtendedClient, ClientEvent } from "../../util/structures";
import { TTScraper } from "tiktok-scraper-ts";

export const event: ClientEvent = {
    name: "tiktokConvert",
    async listen(client: ExtendedClient) {
        client.on("messageCreate", async (message) => {
            
			// Make sure theres a tiktok link in the mesage and it wasnt sent by a bot or anything
			// !message.content.includes("vt.tiktok") || 
			if (message.author.bot || !message.channel || !message.content.includes("tiktok.com")) {
				return
			}

			// delete the original messsage
			await message.delete()

			// let user know that their link is loading
			const tikTokPlaceholder = await message.channel.send("Loading TikTok data... (Might take a few seconds)")

			// grab urls from message and create a clean version of the message content
			const extractUrls = require("extract-urls")
			const turl = require("turl")
			const urls: string[] = extractUrls(message.content)
			var cleanContent = `Sender: ${message.member?.toString()}`
			
			try {
				const scraper = new TTScraper()
				// purge all urls from message content and add no-watermarked links for discord auto-embed to use
				for (var i = 0; i < urls.length; i++) {
					const video = await scraper.video(urls[i])
					cleanContent += `\r\nDescription #${i+1}: ${video.description}`
					cleanContent += `\r\nLink: ${await turl.shorten(video.downloadURL)}`
					cleanContent += '\r\n'
				}

				// make sure the no-watermark conversion worked
				if (!cleanContent.includes("tinyurl")) {
					await tikTokPlaceholder.edit("Something went wrong fetching a direct link to your TikTok. Please contact your server admin / bot dev.")
					console.log(cleanContent)
					return
				}
				
			} catch (e) {
				await tikTokPlaceholder.edit(`Error! Something went wrong.\r\nSender: ${message.member?.toString()}\r\nOrirignal msg: ${message.content}`)
				console.log(e)
				return
			}

			await tikTokPlaceholder.edit({
				content: cleanContent
			})

			return
        })
    }
}