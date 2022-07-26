// # ----------------------------------Imports --------------------------------- #
import { Boomer, SkipEmbedBuilder } from "../structures"
import config from "../../config.json"
import { Player, Queue, SearchResult, Track, UnresolvedTrack } from "erela.js";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "./voice";
import { QueueHelper } from "./queue";
import { PlaylistEmbedBuilder, TrackEmbedBuilder } from "../structures";

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

        var embed = {}

        if (track) {
            embed = new TrackEmbedBuilder(interaction, track, player).toJSON()

            player.queue.add(track)
            console.log("Track added to queue");

        } else if (tracks && result) {
            embed = new PlaylistEmbedBuilder(interaction, result, player).toJSON()

            tracks.forEach(track => {
                player.queue.add(track)
            })
            console.log("Playlist added to queue");
        } 

        if (player.get<boolean>("idle") || !player.playing) {
            player.set("idle", false)
            player.setVolume(config.music.volumeDefault)
            await player.play()
        } 
        
        interaction.editReply({embeds: [embed]})
        this.QH.updatePages(player)
    }

    async play(interaction: CommandInteraction, query: string) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player){
            interaction.reply({content: "No player found...Contact server owner",ephemeral: true})
            return

        } else {
            console.log(`Attempting to play song... Query: ${query}`)
        }
        
        await interaction.deferReply()

        const result = await player.search(query)

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
                break;
        }

        return
    }
    async skip(interaction: CommandInteraction, player: Player, index: number=0, trim_queue=true ) {
        if (player.queue.length = 0 && !player.trackRepeat) {
            await interaction.reply(":notepad_spiral: End of queue - time for your daily dose of idle tunes.")
            player.stop()
        }
        if (player.trackRepeat) {
            const nextTrack = player.queue.current as Track 
            const embed = new SkipEmbedBuilder (interaction,nextTrack,player).toJSON()
            await interaction.reply({content: ":repeat_one: Repeat enabled - repeating song.",embeds:[embed] }) 
            player.seek(0)
            console.log("Skipped (Repeating song).");
            
        } else {
            if (index) {
                const friendlyIndex = index  
                index -= 1
                
                if (index <= 0) {
                    await interaction.reply({content: ":warning: That index is too low! Queue starts at #1.",ephemeral: true})
                    console.log(`Skip failed. Index too low(Expected: >=1. Recieved: ${friendlyIndex})`)
                    return

                } else if (index > player.queue.length) {
                    await interaction.reply({content: `:warning: That index is too high! Queue only ${player.queue.length} items long.`,ephemeral: true})
                    console.log(`Skip failed. Index too low(Expected: <=${player.queue.length}. Recieved: ${friendlyIndex})`)
                    return
                
                } else {
                    if (trim_queue) {
                        console.log(`Skipped queue to track ${index + 1} of ${player.queue.length}`)
                        player.queue.remove(0,index)
                        const nextTrack= player.queue[0]        
                    
                    } else {
                        console.log(`Jumped to track ${index + 1} of ${player.queue.length} in queue.`)
                        const nextTrack= player.queue.remove(index)
                        player.queue.add(nextTrack,0)    
                        
                    }
                }
            } else {
                const nextTrack=player.queue[0] as Track
                console.log("Skipped current track")
                const embed = new SkipEmbedBuilder (interaction,nextTrack,player).toJSON()
                await interaction.reply({embeds: [embed]})  
                player.stop()
            }    

        }
        
        this.QH.updatePages(player) 

    }
}