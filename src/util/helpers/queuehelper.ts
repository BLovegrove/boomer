import { Player, TrackUtils } from "erela.js";
import { Boomer } from "../structures";
import { VoiceHelper } from "./voicehelper";
import config from "../../config.json"
import { EmbedBuilder } from "@discordjs/builders";

class QueueHelper {

    private client: Boomer
    private VH: VoiceHelper

    constructor(client: Boomer) {
        this.client = client
        this.VH = new VoiceHelper(client)
    }

    updatePages(player: Player) {
        player.set('pages', Math.ceil(player.queue.length / config.music.listPageLength))
    }

    embedList(player: Player, page: number) {
        const numPages = player.get<number>('pages')
        const queueStart = (page - 1) * config.music.listPageLength
        var queueEnd = (
            page < numPages
            ? queueStart + (config.music.listPageLength - 1)
            : player.queue.length - 1 
        )

        if (queueEnd == 0) {
            queueEnd += 1
        }

        const track = player.queue.current
        if (!track) {return}

        var modidifiers = ""

        if (player.trackRepeat) {
            modidifiers += ":repeat_one:"
        }

        if (player.queueRepeat) {
            modidifiers+= ":repeat:"
        }

        // TODO: Shuffle goddamnit

        const embed = new EmbedBuilder({
            color: DiscordColors.Blurple,
            title: `Now playing: ***${track.title}***`,
            description: `Page ${page} of ${numPages}. Modifiers: ${modidifiers}`,
            url: track.uri
        })
    }
}