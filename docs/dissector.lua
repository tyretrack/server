pcars_protocol = Proto("PCars", "Project Cars Protocol")

mPacketNumber = ProtoField.uint32("pcars.mPacketNumber", "mPacketNumber", base.DEC)
mCategoryPacketNumber = ProtoField.uint32("pcars.mCategoryPacketNumber", "mCategoryPacketNumber", base.DEC)
mPartialPacketIndex = ProtoField.uint8("pcars.mPartialPacketIndex", "mPartialPacketIndex", base.DEC)
mPartialPacketNumber = ProtoField.uint8("pcars.mPartialPacketNumber", "mPartialPacketNumber", base.DEC)
mPacketType = ProtoField.uint8("pcars.mPacketType", "mPacketType", base.DEC)
mPacketVersion = ProtoField.uint8("pcars.mPacketVersion", "mPacketVersion", base.DEC)

pcars_protocol.fields = {
    mPacketNumber,
    mCategoryPacketNumber,
    mPartialPacketIndex,
    mPartialPacketNumber,
    mPacketType,
    mPacketVersion,
}

function pcars_protocol.dissector(buffer, pinfo, tree)
    local length = buffer:len()
    if length == 0 then return end

    pinfo.cols.protocol = pcars_protocol.name

    local subtree = tree:add(pcars_protocol, buffer(), "Project Cars Protocol Data")

    subtree:add_le(mPacketNumber, buffer(0, 4))
    subtree:add_le(mCategoryPacketNumber, buffer(4, 4))
    subtree:add_le(mPartialPacketIndex, buffer(8, 1))
    subtree:add_le(mPartialPacketNumber, buffer(9, 1))
    subtree:add_le(mPacketVersion, buffer(11, 1))

    local PacketType = buffer(10,1)

    subtree:add_le(mPacketType, PacketType):append_text(" (" .. decode_mPacketType(PacketType:le_uint()) .. ")")
end

function decode_mPacketType(type)
    if type == 0 then return 'eCarPhysics'
    elseif type == 1 then return 'eRaceDefinition'
    elseif type == 2 then return 'eParticipants'
    elseif type == 3 then return 'eTimings'
    elseif type == 4 then return 'eGameState'
    elseif type == 5 then return 'eWeatherState'
    elseif type == 6 then return 'eVehicleNames'
    elseif type == 7 then return 'eTimeStats'
    elseif type == 8 then return 'eParticipantVehicleNamese'
    else return 'unkown'
    end
end

local udp_port = DissectorTable.get("udp.port")
udp_port:add(5606, pcars_protocol)