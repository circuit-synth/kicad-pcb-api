#!/usr/bin/env node

/**
 * MCP Server for KiCAD PCB API
 * 
 * Provides Model Context Protocol interface for AI agent integration
 * with KiCAD PCB manipulation capabilities.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class KiCADPCBServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "kicad-pcb-api",
        version: "0.0.1",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "load_pcb",
          description: "Load a KiCAD PCB file for manipulation",
          inputSchema: {
            type: "object",
            properties: {
              filepath: {
                type: "string",
                description: "Path to the .kicad_pcb file",
              },
            },
            required: ["filepath"],
          },
        },
        {
          name: "create_pcb", 
          description: "Create a new empty PCB",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "save_pcb",
          description: "Save the current PCB to a file",
          inputSchema: {
            type: "object",
            properties: {
              filepath: {
                type: "string",
                description: "Path to save the .kicad_pcb file",
              },
            },
            required: ["filepath"],
          },
        },
        {
          name: "add_footprint",
          description: "Add a footprint to the PCB",
          inputSchema: {
            type: "object",
            properties: {
              reference: {
                type: "string",
                description: "Component reference (e.g., 'R1')",
              },
              footprint_lib: {
                type: "string", 
                description: "Footprint library ID (e.g., 'Resistor_SMD:R_0603_1608Metric')",
              },
              x: {
                type: "number",
                description: "X position in mm",
              },
              y: {
                type: "number",
                description: "Y position in mm", 
              },
              rotation: {
                type: "number",
                description: "Rotation in degrees (default: 0)",
                default: 0,
              },
              value: {
                type: "string",
                description: "Component value (e.g., '10k')",
                default: "",
              },
              layer: {
                type: "string",
                description: "PCB layer (default: 'F.Cu')",
                default: "F.Cu",
              },
            },
            required: ["reference", "footprint_lib", "x", "y"],
          },
        },
        {
          name: "auto_place_components",
          description: "Automatically place components using specified algorithm",
          inputSchema: {
            type: "object",
            properties: {
              algorithm: {
                type: "string",
                enum: ["hierarchical", "spiral", "force_directed"],
                description: "Placement algorithm to use",
                default: "hierarchical",
              },
              component_spacing: {
                type: "number",
                description: "Minimum spacing between components in mm",
                default: 5.0,
              },
              board_width: {
                type: "number",
                description: "Board width in mm",
                default: 100.0,
              },
              board_height: {
                type: "number", 
                description: "Board height in mm",
                default: 100.0,
              },
            },
          },
        },
        {
          name: "get_board_info",
          description: "Get information about the current PCB",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "list_footprints",
          description: "List all footprints on the PCB",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "set_board_outline_rect",
          description: "Set a rectangular board outline",
          inputSchema: {
            type: "object",
            properties: {
              x: {
                type: "number",
                description: "X position of top-left corner in mm",
              },
              y: {
                type: "number",
                description: "Y position of top-left corner in mm",
              },
              width: {
                type: "number",
                description: "Board width in mm",
              },
              height: {
                type: "number",
                description: "Board height in mm",
              },
            },
            required: ["x", "y", "width", "height"],
          },
        },
        {
          name: "get_ratsnest",
          description: "Get the ratsnest (unrouted connections) for the PCB",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        // Execute Python MCP server function
        const result = await this.callPythonFunction(name, args || {});
        return {
          content: [
            {
              type: "text",
              text: result,
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  private async callPythonFunction(
    functionName: string,
    args: Record<string, any>
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      // Build Python command
      const pythonCmd = [
        "-c",
        `
import sys
sys.path.append('${path.join(__dirname, "../python")}')

from kicad_pcb_api.mcp.server import ${functionName}
import asyncio
import json

args = json.loads('${JSON.stringify(args)}')
result = asyncio.run(${functionName}(**args))
print(result, end='')
        `,
      ];

      const python = spawn("python3", pythonCmd, {
        stdio: ["pipe", "pipe", "pipe"],
      });

      let stdout = "";
      let stderr = "";

      python.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      python.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      python.on("close", (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`Python execution failed: ${stderr}`));
        }
      });

      python.on("error", (error) => {
        reject(error);
      });
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("KiCAD PCB API MCP Server running on stdio");
  }
}

// Start the server
const server = new KiCADPCBServer();
server.run().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});