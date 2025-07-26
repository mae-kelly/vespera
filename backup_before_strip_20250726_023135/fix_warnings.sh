#!/bin/bash

# Fix unused import in okx_executor.rs
sed -i.bak '1s/use std::collections::HashMap;//' src/okx_executor.rs

# Fix deprecated base64 functions in auth.rs
sed -i.bak 's/base64::decode/base64::engine::general_purpose::STANDARD.decode/g' src/auth.rs
sed -i.bak 's/base64::encode/base64::engine::general_purpose::STANDARD.encode/g' src/auth.rs

# Add the proper import for base64 engine
sed -i.bak '3i\
use base64::Engine;' src/auth.rs

echo "✅ Warnings fixed"
