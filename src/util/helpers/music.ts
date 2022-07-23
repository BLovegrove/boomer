// # ----------------------------------Imports --------------------------------- #
import { Boomer } from "../structures"
import config from "../../config.json"
import { Player, SearchResult } from "erela.js";
import { CommandInteraction,GuildMember, VoiceStateManager } from "discord.js";
import { VoiceHelper } from "./voice";
import { rxUrl } from "./regex";

// # ----------------------------------Config ---------------------------------- #

export class Music {

    private client: Boomer;
    private VH : VoiceHelper

    constructor(client: Boomer) {
        this.client = client;
        this.VH = new VoiceHelper(client)

    }

    async play( interaction: CommandInteraction, query: string) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player){
            interaction.reply({content: "No player found...Contact server owner",ephemeral: true})
            return null
        } else {
            console.log(`Attempting to play song... Query: ${query}`)
            
        } 
        
        interaction.deferReply()

        if (!rxUrl.test(query)) {
            query = `ytsearch:${query}`
        }

        const result = await player.search(query)

        switch(result.loadType) {
            case "NO_MATCHES":
                await interaction.editReply({content: "404 Song not found! Try something else."});
                return;
            case "SEARCH_RESULT":
                // const tracks = result.tracks;
                break;
            default:
                await interaction.editReply({content: "Something unexpected happen. Contact your server owner immediately and let them know the exact command you tried to run."});
                console.log(`Load type for play request defaulted. query '${query}' result as follows:`);
                console.log(result);
                return;
        }

        if (result.playlist) {  
           const tracks = result.tracks
           const info = result.info 
        }
        

    }
}