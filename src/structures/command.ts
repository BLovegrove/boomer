import { CommandInteraction, InteractionResponse } from "discord.js"
import { Boomer } from "./boomer"

export type Command = {
    data: any,
    execute(interaction: CommandInteraction, client: Boomer): Promise<InteractionResponse>
}