import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("leave")
        .setDescription("Clears the queue and leaves the call.")
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        
        if (!client.playerExists) {
            interaction.reply({ content: "He's not playing anything - why are you even trying this?" , ephemeral: true})
        } else {
            const VH = new VoiceHandler(client)
            const player = await VH.ensureVoice(interaction)
            if (!player) {
                return
            }

            VH.disconnect(player)
            interaction.reply("'Aight I'mma head out... o7 (Clearing queue and leaving call)")
        }
    }
}