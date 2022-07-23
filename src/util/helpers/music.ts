// # ----------------------------------Imports --------------------------------- #
import { Boomer } from "../structures"
import config from "../../config.json"
import { Player, SearchResult, Track } from "erela.js";
import { CommandInteraction,GuildMember, Interaction, VoiceStateManager } from "discord.js";
import { VoiceHelper } from "./voicehelper";
import { rxUrl } from "./regex";

// # ----------------------------------Config ---------------------------------- #

interface AddTrackOptions {
    player: Player
    interaction?: CommandInteraction
    track?: Track
    tracks?: Track[]
    
}

export class Music {

    private client: Boomer;
    private VH: VoiceHelper

    constructor(client: Boomer) {
        this.client = client;
        this.VH = new VoiceHelper(client)

    }

    private async addTrack ({player,interaction,track,tracks}: AddTrackOptions ) {
        if (track) {
            player.queue.add(track)
            console.log("Track added to queue");
        } else if (tracks) {
            tracks.forEach(track => {
                player.queue.add(track)
            })
        } 

        if (player.get<boolean>("idle") || !player.playing ) {
            player.set("idle",false)
            player.setVolume(config.music.volumeDefault)
            await player.play()
        } 
        //TODO: add queue manager.update pages. thax 
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
        //TODO: Add new track embed

        switch(result.loadType) {
            case "LOAD_FAILED":
                interaction.editReply( "Failed to load track, please use a URL or different search term");
                break;
            case "NO_MATCHES":
                interaction.editReply("404 Song not found! Try something else.");
                break;
            case "SEARCH_RESULT":
                var track = result.tracks.at(0);
                this.addTrack({player:player,track:track})
                break;
            case "TRACK_LOADED":
                var track = result.tracks.at(0);
                this.addTrack({player:player,track:track})
                break;
            case "PLAYLIST_LOADED":
                var tracks = result.tracks;
                this.addTrack({player:player,tracks:tracks})
                break;
            default:
                await interaction.editReply("Something unexpected happen. Contact your server owner immediately and let them know the exact command you tried to run.");
                console.log(`Load type for play request defaulted. query '${query}' result as follows:`);
                console.log(result);
                return;
        }
    }
}