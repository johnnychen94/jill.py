JULIA_VERSION=$1
echo "Installing specific Julia version ${JULIA_VERSION}"
python -m jill install ${JULIA_VERSION} --confirm

julia -v
major=$(echo ${JULIA_VERSION} | cut -d. -f1)
minor=$(echo ${JULIA_VERSION} | cut -d. -f1-2)
julia-${JULIA_VERSION} -v
julia-${major} -v
julia-${minor} -v

echo "Testing if the version is correct"
[[ $(julia-${JULIA_VERSION} -v) == "julia version ${JULIA_VERSION}" ]]
