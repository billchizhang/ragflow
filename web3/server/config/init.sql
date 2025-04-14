-- Create Users table
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- Create Documents table
CREATE TABLE Documents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    title NVARCHAR(255) NOT NULL,
    content NVARCHAR(MAX),
    file_path NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Create Embeddings table
CREATE TABLE Embeddings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id INT NOT NULL,
    embedding_vector VARBINARY(MAX) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (document_id) REFERENCES Documents(id)
);

-- Create Index for faster lookups
CREATE INDEX idx_documents_user_id ON Documents(user_id);
CREATE INDEX idx_embeddings_document_id ON Embeddings(document_id);

-- Create stored procedure for document search
CREATE PROCEDURE SearchDocuments
    @query_vector VARBINARY(MAX),
    @user_id INT,
    @top_k INT = 10
AS
BEGIN
    SELECT TOP (@top_k)
        d.id,
        d.title,
        d.content,
        d.file_path,
        d.created_at,
        d.updated_at,
        -- Calculate cosine similarity
        CAST(1.0 - (CAST(SUM(e.embedding_vector * @query_vector) AS FLOAT) / 
            (SQRT(SUM(e.embedding_vector * e.embedding_vector)) * 
             SQRT(SUM(@query_vector * @query_vector)))) AS FLOAT) AS similarity
    FROM Documents d
    JOIN Embeddings e ON d.id = e.document_id
    WHERE d.user_id = @user_id
    GROUP BY d.id, d.title, d.content, d.file_path, d.created_at, d.updated_at
    ORDER BY similarity ASC;
END;

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token VARCHAR(6) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert test user for development/testing
-- email: test@test.com, password: test123 (bcrypt hashed)
INSERT INTO users (email, password, first_name, last_name) 
VALUES ('test@test.com', '$2a$10$NMXGoYIZ4vGAb2BHmfYtcum3OyN0CkGQs.4JtEWDSf.28dMJU2TOa', 'Test', 'User')
ON DUPLICATE KEY UPDATE id=id; 