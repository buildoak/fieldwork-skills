# Story JSON Schema

Canonical schema used by `scripts/decompose.py` for `story.json` generation.

## JSON Schema (Canonical)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "story.json schema",
  "type": "object",
  "required": [
    "title",
    "logline",
    "style",
    "aspect_ratio",
    "target_duration_sec",
    "tier",
    "characters",
    "scenes",
    "shots"
  ],
  "properties": {
    "title": {
      "type": "string",
      "minLength": 3
    },
    "logline": {
      "type": "string",
      "minLength": 10
    },
    "style": {
      "type": "string",
      "enum": [
        "cinematic",
        "anime",
        "documentary",
        "social_media"
      ]
    },
    "aspect_ratio": {
      "type": "string",
      "enum": [
        "16:9",
        "9:16",
        "1:1"
      ]
    },
    "target_duration_sec": {
      "type": "integer",
      "minimum": 6,
      "maximum": 180
    },
    "tier": {
      "type": "string",
      "enum": [
        "budget",
        "standard",
        "premium",
        "ultra"
      ]
    },
    "theme": {
      "type": "string"
    },
    "tone": {
      "type": "string"
    },
    "characters": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/character"
      }
    },
    "scenes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/scene"
      }
    },
    "shots": {
      "type": "array",
      "minItems": 2,
      "items": {
        "$ref": "#/$defs/shot"
      }
    },
    "audio": {
      "type": "object",
      "properties": {
        "voiceover_script": {
          "type": "string"
        },
        "music_direction": {
          "type": "string"
        },
        "sfx_notes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "additionalProperties": true
    }
  },
  "$defs": {
    "character": {
      "type": "object",
      "required": [
        "id",
        "name",
        "role",
        "description",
        "appearance",
        "wardrobe"
      ],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z0-9_\\-]+$"
        },
        "name": {
          "type": "string"
        },
        "role": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "age": {
          "type": [
            "integer",
            "string"
          ]
        },
        "ethnicity": {
          "type": "string"
        },
        "gender": {
          "type": "string"
        },
        "appearance": {
          "type": "object",
          "properties": {
            "skin_tone": {
              "type": "string"
            },
            "face_shape": {
              "type": "string"
            },
            "eye_color": {
              "type": "string"
            },
            "hair_length": {
              "type": "string"
            },
            "hair_color": {
              "type": "string"
            },
            "hair_style": {
              "type": "string"
            },
            "build": {
              "type": "string"
            },
            "distinguishing_features": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "accessories": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "additionalProperties": true
        },
        "wardrobe": {
          "type": "object",
          "properties": {
            "top": {
              "type": "string"
            },
            "bottom": {
              "type": "string"
            },
            "shoes": {
              "type": "string"
            }
          },
          "additionalProperties": true
        },
        "consistency_notes": {
          "type": "string"
        }
      },
      "additionalProperties": true
    },
    "scene": {
      "type": "object",
      "required": [
        "scene_id",
        "summary",
        "location",
        "shot_ids"
      ],
      "properties": {
        "scene_id": {
          "type": "string",
          "pattern": "^scene_[0-9]{2,3}$"
        },
        "summary": {
          "type": "string"
        },
        "location": {
          "type": "string"
        },
        "time_of_day": {
          "type": "string"
        },
        "mood": {
          "type": "string"
        },
        "palette": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "beats": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "shot_ids": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 1
        }
      },
      "additionalProperties": true
    },
    "shot": {
      "type": "object",
      "required": [
        "shot_id",
        "scene_id",
        "duration_sec",
        "prompt",
        "keyframe_prompt",
        "motion_prompt",
        "camera",
        "characters",
        "transition_to_next"
      ],
      "properties": {
        "shot_id": {
          "type": "string",
          "pattern": "^shot_[0-9]{2,3}$"
        },
        "scene_id": {
          "type": "string",
          "pattern": "^scene_[0-9]{2,3}$"
        },
        "start_sec": {
          "type": "number",
          "minimum": 0
        },
        "end_sec": {
          "type": "number",
          "minimum": 0
        },
        "duration_sec": {
          "type": "number",
          "minimum": 2,
          "maximum": 10
        },
        "prompt": {
          "type": "string"
        },
        "keyframe_prompt": {
          "type": "string"
        },
        "motion_prompt": {
          "type": "string"
        },
        "negative_prompt": {
          "type": "string"
        },
        "camera": {
          "type": "object",
          "properties": {
            "framing": {
              "type": "string"
            },
            "movement": {
              "type": "string"
            },
            "lens": {
              "type": "string"
            }
          },
          "additionalProperties": true
        },
        "location": {
          "type": "string"
        },
        "mood": {
          "type": "string"
        },
        "characters": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "continuity_notes": {
          "type": "string"
        },
        "transition_to_next": {
          "type": "object",
          "required": [
            "type",
            "duration_sec"
          ],
          "properties": {
            "type": {
              "type": "string",
              "enum": [
                "cut",
                "fade",
                "dissolve",
                "wipe_left",
                "wipe_right",
                "slide_left",
                "slide_right"
              ]
            },
            "duration_sec": {
              "type": "number",
              "minimum": 0,
              "maximum": 2
            }
          },
          "additionalProperties": true
        }
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": true
}
```
