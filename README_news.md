
## News 🔥🔥🔥

- [04-23-2025] Data Formulator 0.2: working with *large* data 📦📦📦
  - Explore large data by:
    1. Upload large data file to the local database (powered by [DuckDB](https://github.com/duckdb/duckdb)).
    2. Use drag-and-drop to specify charts, and Data Formulator dynamically fetches data from the database to create visualizations (with ⚡️⚡️⚡️ speeds).
    3. Work with AI agents: they generate SQL queries to transform the data to create rich visualizations!
    4. Anchor the result / follow up / create a new branch / join tables; let's dive deeper. 
  - Checkout the demos at [[https://github.com/microsoft/data-formulator/releases/tag/0.2]](https://github.com/microsoft/data-formulator/releases/tag/0.2)
  - Improved overall system performance, and enjoy the updated derive concept functionality.

- [03-20-2025] Data Formulator 0.1.7: Anchoring ⚓︎
  - Anchor an intermediate dataset, so that followup data analysis are built on top of the anchored data, not the original one.
  - Clean a data and work with only the cleaned data; create a subset from the original data or join multiple data, and then go from there. AI agents will be less likely to get confused and work faster. ⚡️⚡️
  - Check out the demos at [[https://github.com/microsoft/data-formulator/releases/tag/0.1.7]](https://github.com/microsoft/data-formulator/releases/tag/0.1.7)
  - Don't forget to update Data Formulator to test it out!

- [02-20-2025] Data Formulator 0.1.6 released! 
  - Now supports working with multiple datasets at once! Tell Data Formulator which data tables you would like to use in the encoding shelf, and it will figure out how to join the tables to create a visualization to answer your question. 🪄
  - Checkout the demo at [[https://github.com/microsoft/data-formulator/releases/tag/0.1.6]](https://github.com/microsoft/data-formulator/releases/tag/0.1.6).
  - Update your Data Formulator to the latest version to play with the new features.

- [02-12-2025] More models supported now!
  - Now supports OpenAI, Azure, Ollama, and Anthropic models (and more powered by [LiteLLM](https://github.com/BerriAI/litellm));
  - Models with strong code generation and instruction following capabilities are recommended (gpt-4o, claude-3-5-sonnet etc.);
  - You can store API keys in `api-keys.env` to avoid typing them every time (see template `api-keys.env.template`).
  - Let us know which models you have good/bad experiences with, and what models you would like to see supported! [[comment here]](https://github.com/microsoft/data-formulator/issues/49)

- [11-07-2024] Minor fun update: data visualization challenges!
  - We added a few visualization challenges with the sample datasets. Can you complete them all? [[try them out!]](https://github.com/microsoft/data-formulator/issues/53#issue-2641841252)
  - Comment in the issue when you did, or share your results/questions with others! [[comment here]](https://github.com/microsoft/data-formulator/issues/53)

- [10-11-2024] Data Formulator python package released! 
  - You can now install Data Formulator using Python and run it locally, easily. [[check it out]](#get-started).
  - Our Codespaces configuration is also updated for fast start up ⚡️. [[try it now!]](https://codespaces.new/microsoft/data-formulator?quickstart=1)
  - New experimental feature: load an image or a messy text, and ask AI to parse and clean it for you(!). [[demo]](https://github.com/microsoft/data-formulator/pull/31#issuecomment-2403652717)
  
- [10-01-2024] Initial release of Data Formulator, check out our [[blog]](https://www.microsoft.com/en-us/research/blog/data-formulator-exploring-how-ai-can-help-analysts-create-rich-data-visualizations/) and [[video]](https://youtu.be/3ndlwt0Wi3c)!


