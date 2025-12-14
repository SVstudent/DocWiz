# MCP Server Setup for DocWiz

This directory contains MCP (Model Context Protocol) server configurations for DocWiz.

## Configured Servers

### Freepik MCP Server

The Freepik MCP server provides access to Freepik's image generation and creative assets API.

**Configuration**: `mcp.json`

```json
{
  "mcpServers": {
    "mcp-freepik": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.freepik.com/mcp", "--header", "x-freepik-api-key:${FREEPIK_API_KEY}"],
      "env": {
        "FREEPIK_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Setup Instructions

### 1. Get Freepik API Key

1. Go to [Freepik Developer Portal](https://www.freepik.com/api)
2. Sign up or log in
3. Create a new API key
4. Copy the API key

### 2. Update MCP Configuration

Edit `.kiro/settings/mcp.json` and replace `test_freepik_key` with your actual API key:

```json
{
  "mcpServers": {
    "mcp-freepik": {
      "env": {
        "FREEPIK_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### 3. Verify MCP Server

The MCP server will automatically connect when you use Kiro. You can verify it's working by:

1. Opening the MCP Server view in Kiro
2. Checking that `mcp-freepik` shows as "Connected"
3. Testing a Freepik API call through the backend

## Using Freepik MCP in Code

The Freepik MCP server is integrated into the backend through `backend/app/services/freepik_client.py`.

Example usage:

```python
from app.services.freepik_client import FreepikClient

freepik = FreepikClient()

# Generate cost infographic
infographic = await freepik.generate_cost_infographic(
    cost_breakdown=cost_data,
    format="png"
)

# Generate enhanced visualization
enhanced_image = await freepik.enhance_image(
    image_url=original_url,
    style="medical_professional"
)
```

## Capabilities

The Freepik MCP server provides:

- **Image Generation**: Create custom graphics and infographics
- **Image Enhancement**: Improve image quality and styling
- **Template Access**: Use pre-designed templates for medical visualizations
- **Asset Library**: Access Freepik's vast library of medical icons and graphics

## Troubleshooting

**Error: "MCP server not connected"**
- Check that `npx` is installed (comes with Node.js)
- Verify your Freepik API key is valid
- Check network connectivity

**Error: "Invalid API key"**
- Ensure you copied the full API key
- Check for extra spaces or quotes
- Verify the key hasn't expired

**Error: "Rate limit exceeded"**
- Freepik has rate limits on free tier
- Wait a few minutes and try again
- Consider upgrading to paid tier for hackathon

## Auto-Approval

To avoid manual approval prompts for Freepik operations, add tool names to `autoApprove`:

```json
{
  "mcpServers": {
    "mcp-freepik": {
      "autoApprove": [
        "generate_image",
        "enhance_image",
        "search_assets"
      ]
    }
  }
}
```

## Disabling the Server

To temporarily disable the Freepik MCP server:

```json
{
  "mcpServers": {
    "mcp-freepik": {
      "disabled": true
    }
  }
}
```

## Resources

- [Freepik API Documentation](https://www.freepik.com/api/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Kiro MCP Guide](https://docs.kiro.ai/mcp)
