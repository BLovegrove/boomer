import { Client, ClientOptions, Collection } from "discord.js";
import { Manager } from "erela.js";
import { Command } from "./command";
import config from "../../config.json"
import { CommandHelper } from "../helpers/command";
import path from "path"

export class ExtendedClient extends Client {

    commands: Collection<String, Command>
    manager: Manager
    private _playerExists: boolean

    constructor(options: ClientOptions, manager: Manager) {
        super(options);
        
        this.manager = manager
        this._playerExists = false
        
        // grab the command files and generate a collection from them
        this.commands = CommandHelper.load(path.join(__dirname, "../../commands"))
        // register the commands with the discord API to display them on the server
        CommandHelper.register(this.commands)
    }

    get playerExists() {
        this._playerExists = this.manager.players.keyArray().length != 0 ? true : false
        return this._playerExists
    }

    async connect() {
        if (config.bot.devMode) {
            await this.login(config.dev.token)
        } else {
            await this.login(config.bot.token);
        }
    };
};