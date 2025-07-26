#!/bin/bash

# i unused import in ok_eecutor.rs
sed -i.bak 's/use std::collections::HashMap;//' src/ok_eecutor.rs

# i deprecated base functions in auth.rs
sed -i.bak 's/base::decode/base::engine::general_purpose::STANDARD.decode/g' src/auth.rs
sed -i.bak 's/base::encode/base::engine::general_purpose::STANDARD.encode/g' src/auth.rs

# Add the proper import for base engine
sed -i.bak 'i
use base::ngine;' src/auth.rs

echo "✅ Warnings fied"
