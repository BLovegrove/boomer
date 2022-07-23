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

    
}