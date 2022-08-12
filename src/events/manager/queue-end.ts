import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, ClientEvent } from "../../util/structures";
import config from "../../config.json"
import { TextChannel } from "discord.js";
import { Track } from "erela.js";

export const event: ClientEvent = {
    name: "queueEnd",
    async listen(client: ExtendedClient) {

        // fires whenever the queue runs out fo tracks
        client.manager.on("queueEnd", async node => {
            const player = VoiceHandler.fetchPlayer(client)
            const VH = new VoiceHandler(client)
            if (!player) {
                return
            }

            player.setVolume(config.music.volumeIdle)

            const results = await player.search(config.music.idleTrack)

            if (!results || !results.tracks || results.loadType != "TRACK_LOADED") {
                player.queue.clear()
                VH.disconnect(player)

                if (!player.textChannel) {
                    console.log("Couldnt find a text channel when queuing idle track.")
                    return
                }

                const channel = client.channels.cache.get(player.textChannel) as TextChannel
                channel.send(":warning: Nothing found when looking for idle music! look for a new video.")
                return
            }

            player.set('idle', true)
            player.setTrackRepeat(true)

            const track = results.tracks.at(0) as Track
            console.log(track)
            player.queue.add(track, 0)

            if (!player.playing) {
                await player.play()
            }
        })

    }
}