/**
 * Lightweight XOR-based obfuscation for storing API keys in the session.
 *
 * This is NOT cryptographic security — it simply prevents casual shoulder-
 * surfing. Real encryption happens server-side with AES-256.
 */

const SESSION_KEY = "ucl-scout-session-key";

const getSessionSecret = (): string => {
  let secret = sessionStorage.getItem(SESSION_KEY);
  if (!secret) {
    secret = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, secret);
  }
  return secret;
};

export const encryptKey = (plaintext: string): string => {
  const secret = getSessionSecret();
  const encoded = Array.from(plaintext)
    .map((char, i) =>
      String.fromCharCode(
        char.charCodeAt(0) ^ secret.charCodeAt(i % secret.length),
      ),
    )
    .join("");
  return btoa(encoded);
};

export const decryptKey = (ciphertext: string): string => {
  const secret = getSessionSecret();
  const decoded = atob(ciphertext);
  return Array.from(decoded)
    .map((char, i) =>
      String.fromCharCode(
        char.charCodeAt(0) ^ secret.charCodeAt(i % secret.length),
      ),
    )
    .join("");
};
