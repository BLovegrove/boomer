import { REST } from "@discordjs/rest";
import { Collection, Routes } from "discord.js";
import { Command } from "../types";
import fs from "fs";
import config from "../config.json"


// read commands dirs for command modules
export function loadCommands(commandPath: fs.PathLike) {
    // init empty commands collection

    const commands = new Collection<String, Command>();
    fs.readdirSync(commandPath).forEach(dir => {
        // both file.endswith needed for dev vs production running
        const files = fs.readdirSync(`${commandPath}/${dir}/`).filter(file => (file.endsWith('.js') || file.endsWith('.ts')));

        // add command module files to collection
        for (const file of files) {
            const { command } = require(`${commandPath}/${dir}/${file}`);
            commands.set(command.data.name, command);
        }
    });

    return commands;
}


// register the slash commands with discord (globally)
const rest = new REST({ version: '9' }).setToken(config.token);
export async function register(commands: Collection<String, Command>) {

    try {
        console.log('Started refreshing application (/) commands.');

        const commandsData: any[] = []
        commands.forEach(command => {
            commandsData.push(command.data.toJSON())
        })
        await rest.put(Routes.applicationCommands(config.clientID), { body: commandsData });

        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
}