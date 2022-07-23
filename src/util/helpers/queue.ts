import { VoiceStateManager } from "discord.js";
import { Player } from "erela.js";
import { Boomer } from "../structures";
import { VoiceStateHelper } from "./voice";
 

class QueueHelper {

    client: Boomer
    vsh: VoiceStateHelper

    constructor(client: Boomer) {
        this.client = client
        this.vsh = new VoiceStateHelper(client)
    }

    update_pages(player: Player) {

    }
}