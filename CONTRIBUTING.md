# How to Contribute

We welcome contributions from everyone! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is appreciated.

## Ways to Contribute

### 🚀 Pull Requests
1. **Fork the Repository**: Create your own copy of the project.
2. **Create a Branch**: Work on a new branch for your changes (`git checkout -b feature/cool-new-feature`).
3. **Make Changes**: Implement your fix or feature.
4. **Follow Standards**: Ensure your code is clean, documented, and follows the project's structure.
5. **Submit a PR**: Open a Pull Request from your branch back to our `main` branch.

### 💡 Feature Suggestions
- Have an idea for a new feature? Open an issue using the **Feature Request** template.
- Describe the solution you'd like and any alternatives you've considered.

### 📖 Documentation
- Help us keep the `README.md` and other guides accurate and easy to understand.

## Getting Started
1. Clone the repository locally.
2. Ensure Python 3.x is installed.
3. Install dependencies for building: `pip install pyinstaller`.
4. Check the `README.md` for tool usage details.

## Releasing (Maintainers Only)

To create a new release:
1. **Tag the Release**: Tag the final commit on `main` with a version number (e.g., `git tag -a v1.0.0 -m "Release v1.0.0"`).
2. **Push the Tag**: `git push origin v1.0.0`.
3. **GitHub Release**:
    - Go to **Releases** on GitHub and select **Draft a new release**.
    - Link it to the pushed tag.
    - **Note**: GitHub automatically creates `.zip` and `.tar.gz` source archives for you. **Do not manually upload a zip of the root directory.**
    - **Attach Assets**: Manually upload the `mx--cleanuserlib.exe` file as a release asset so users can download the standalone binary without needing Python.

Thank you for being part of the community!
