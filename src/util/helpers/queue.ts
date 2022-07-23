import { Player } from "erela.js";
import { Boomer } from "../structures";
import { VoiceHelper } from "./voice";
 

class QueueHelper {

    private client: Boomer
    private VH: VoiceHelper

    constructor(client: Boomer) {
        this.client = client
        this.VH = new VoiceHelper(client)
    }

    update_pages(player: Player) {
        player.set('pages', Math.ceil(player.queue.length))
    }
}