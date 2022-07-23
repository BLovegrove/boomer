import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers/voicehelper";
import { Boomer, Command } from "../../util/structures";

// export var must always be 'command' - see 'add command module files to collection' in index.ts
// : Command type adds strong typing for interaction and client args! Thank god for typescript
export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("erelatest")
        .setDescription("Prints an example player search result to console for debugging"),

    async execute(interaction: CommandInteraction, client: Boomer) {

        const VH = new VoiceHelper(client)
        const player = await VH.ensureVoice(interaction)

        if (!player) {
            interaction.reply("Something went wrong! Couldnt create/fetch the player.")
            return

        } else {

            console.log("Text search result:");
            console.log(await player.search("Rick Astley"));

            console.log("YT Track result:")
            console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ"));

            console.log("YT Playlist result:");
            console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLCiNIjl_KpQhFwQA3G19w1nmhEOlZQsGF"))
            
            return
        }
        
    }
}