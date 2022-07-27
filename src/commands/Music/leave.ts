import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("leave")
        .setDescription("Clears the queue and leaves the call.")
        ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        
        if (!client.playerExists) {
            interaction.reply({ content: "He's not playing anything - why are you even trying this?" , ephemeral: true})
        } else {
            const VH = new VoiceHelper(client)
            const player = await VH.ensureVoice(interaction)
            if (!player) {
                return
            }

            VH.disconnect(player)
            interaction.reply("'Aight I'mma head out... o7 (Clearing queue and leaving call)")
        }
    }
}