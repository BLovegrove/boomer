import { Player } from "erela.js";
import { Boomer } from "../structures";
import { VoiceHelper } from "./voice";
 

class QueueHelper {

    client: Boomer
    vsh: VoiceHelper

    constructor(client: Boomer) {
        this.client = client
        this.vsh = new VoiceHelper(client)
    }

    update_pages(player: Player) {

    }
}