// # ----------------------------------Imports --------------------------------- #
import { Boomer } from "../structures"
import config from "../../config.json"
import { Player, SearchResult, Track } from "erela.js";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "./voicehelper";
import { RxUrl } from "./regex";
import { QueueHelper } from "./queuehelper";
import { PlaylistEmbedBuilder, TrackEmbedBuilder } from "../structures/embedbuilders";

// # ----------------------------------Config ---------------------------------- #

interface IAddTrackOptions {
    player: Player
    interaction: CommandInteraction
    track?: Track
    tracks?: Track[]
    result?: SearchResult
}

export class MusicHelper {

    private client: Boomer;
    private VH: VoiceHelper
    QH: QueueHelper

    constructor(client: Boomer) {
        this.client = client;
        this.VH = new VoiceHelper(client)
        this.QH = new QueueHelper(client)
    }

    private async addTrack ({player,interaction,track,tracks,result}: IAddTrackOptions ) {
        if (track) {
            interaction.editReply({
                embeds: [
                    new TrackEmbedBuilder(interaction, track, player).toJSON()
                ]
            })

            player.queue.add(track)
            console.log("Track added to queue");

        } else if (tracks && result) {
            interaction.editReply({
                embeds: [
                    new PlaylistEmbedBuilder(interaction, result, player).toJSON()
                ]
            })

            tracks.forEach(track => {
                player.queue.add(track)
            })
            console.log("Playlist added to queue");
        } 

        if (player.get<boolean>("idle") || !player.playing ) {
            player.set("idle",false)
            player.setVolume(config.music.volumeDefault)
            await player.play()
        } 
        
        this.QH.updatePages(player)
    }

    async play(interaction: CommandInteraction, query: string) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player){
            interaction.reply({content: "No player found...Contact server owner",ephemeral: true})
            return null
        } else {
            console.log(`Attempting to play song... Query: ${query}`)
            
        } 
        
        interaction.deferReply()

        if (!RxUrl.test(query)) {
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
                var track = result.tracks.at(0) as Track;
                this.addTrack({player, interaction, track:track})
                break;
            case "TRACK_LOADED":
                var track = result.tracks.at(0) as Track
                this.addTrack({player, interaction, track: track})
                break;
            case "PLAYLIST_LOADED":
                var tracks = result.tracks;
                this.addTrack({player, interaction, tracks: tracks, result: result})
                break;
            default:
                await interaction.editReply("Something unexpected happen. Contact your server owner immediately and let them know the exact command you tried to run.");
                console.log(`Load type for play request defaulted. query '${query}' result as follows:`);
                console.log(result);
                return;
        }
    }
}