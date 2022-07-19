import { Client, CommandInteraction, InteractionResponse, SlashCommandBuilder } from "discord.js"

export type Command = {
    data: SlashCommandBuilder,
    execute(interaction: CommandInteraction, client?:Client): Promise<InteractionResponse>
}