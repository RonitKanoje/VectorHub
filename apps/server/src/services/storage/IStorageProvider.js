export class IStorageProvider {
  /**
   * Save a file
   * @param {Object} file - The file object from Multer
   * @param {String} userId - User ID
   * @param {String} threadId - Thread ID
   * @returns {Promise<String>} - The stored file path or URL
   */
  async saveFile(file, userId, threadId) {
    throw new Error("Method 'saveFile()' must be implemented.");
  }

  /**
   * Delete a file
   * @param {String} filePath - The file path or URL to delete
   * @returns {Promise<void>}
   */
  async deleteFile(filePath) {
    throw new Error("Method 'deleteFile()' must be implemented.");
  }
}
