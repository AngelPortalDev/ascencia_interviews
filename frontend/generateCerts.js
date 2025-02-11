import { createCA, createCert } from "mkcert";
import fs from "fs";
import path from "path";

const certsDir = path.resolve(process.cwd(), "certs");

// Create the certs directory if it doesn't exist
if (!fs.existsSync(certsDir)) {
  fs.mkdirSync(certsDir, { recursive: true });
}

const generateCerts = async () => {
  try {
    const ca = await createCA({
      organization: "Local CA",
      countryCode: "IN",
      state: "Maharashtra",
      locality: "Mumbai",
      validity: 365,
    });

    const cert = await createCert({
      ca: { key: ca.key, cert: ca.cert },
      domains: ["127.0.0.1", "localhost", "192.168.1.15"], 
      validity: 365,
    });

    // Save the generated certificates
    fs.writeFileSync(path.join(certsDir, "localhost-key.pem"), cert.key);
    fs.writeFileSync(path.join(certsDir, "localhost-cert.pem"), cert.cert);
    fs.writeFileSync(path.join(certsDir, "ca-cert.pem"), ca.cert);

    console.log("Certificates generated successfully!");
  } catch (error) {
    console.error("Error generating certificates:", error);
  }
};

// Run the certificate generation
generateCerts();
